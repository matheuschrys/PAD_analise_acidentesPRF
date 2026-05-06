from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


SCHEMA_PANDAS = {
    "id": "Int64",
    "dia_semana": "category",
    "uf": "category",
    "br": "string",
    "municipio": "category",
    "causa_acidente": "category",
    "tipo_acidente": "category",
    "fase_dia": "category",
    "condicao_metereologica": "category",
    "tipo_pista": "category",
    "tracado_via": "category",
    "ilesos": "Int16",
    "feridos_leves": "Int16",
    "feridos_graves": "Int16",
    "mortos": "Int8",
}

DATE_COLUMNS = ["data_inversa"]
TIME_COLUMNS = ["horario"]
NUMERIC_NON_NEGATIVE_COLUMNS = ["ilesos", "feridos_leves", "feridos_graves", "mortos"]


def expected_columns() -> list[str]:
    """Retorna as colunas esperadas no dataset bruto."""
    return list(SCHEMA_PANDAS.keys()) + DATE_COLUMNS + TIME_COLUMNS


def available_columns(csv_path: str | Path, sep: str = ";", encoding: str = "latin1") -> list[str]:
    """Le apenas o cabecalho do CSV para descobrir as colunas disponiveis."""
    return list(pd.read_csv(csv_path, sep=sep, encoding=encoding, nrows=0).columns)


def columns_to_read(csv_path: str | Path, sep: str = ";", encoding: str = "latin1") -> list[str]:
    """Cruza schema esperado com colunas existentes para evitar erro por coluna ausente."""
    present_columns = set(available_columns(csv_path, sep=sep, encoding=encoding))
    return [column for column in expected_columns() if column in present_columns]


def validate_required_columns(
    csv_paths: Iterable[str | Path],
    required_columns: Iterable[str] | None = None,
    sep: str = ";",
    encoding: str = "latin1",
) -> pd.DataFrame:
    """Gera relatorio de colunas ausentes por arquivo CSV."""
    required = list(required_columns or expected_columns())
    rows = []

    for csv_path in csv_paths:
        path = Path(csv_path)
        present = set(available_columns(path, sep=sep, encoding=encoding))
        missing = [column for column in required if column not in present]
        rows.append(
            {
                "arquivo": path.name,
                "colunas_esperadas": len(required),
                "colunas_ausentes": len(missing),
                "lista_colunas_ausentes": ", ".join(missing) if missing else "Nenhuma",
            }
        )

    return pd.DataFrame(rows)


def validate_dataframe_quality(df: pd.DataFrame, schema: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Cria relatorios simples de tipos, nulos e valores invalidos."""
    schema = schema or SCHEMA_PANDAS

    type_rows = []
    for column, expected_type in schema.items():
        if column not in df.columns:
            type_rows.append(
                {
                    "coluna": column,
                    "tipo_esperado": expected_type,
                    "tipo_encontrado": "AUSENTE",
                    "status": "ausente",
                }
            )
            continue

        found_type = str(df[column].dtype)
        type_rows.append(
            {
                "coluna": column,
                "tipo_esperado": expected_type,
                "tipo_encontrado": found_type,
                "status": "ok" if found_type == expected_type else "verificar",
            }
        )

    null_report = (
        df.isna()
        .sum()
        .reset_index()
        .rename(columns={"index": "coluna", 0: "qtd_nulos"})
        .sort_values("qtd_nulos", ascending=False)
    )
    null_report["percentual_nulos"] = (null_report["qtd_nulos"] / len(df) * 100).round(2)

    invalid_rows = []
    for column in NUMERIC_NON_NEGATIVE_COLUMNS:
        if column in df.columns:
            invalid_rows.append(
                {
                    "coluna": column,
                    "regra": "valor >= 0",
                    "valores_invalidos": int((df[column] < 0).sum()),
                }
            )

    if "data_inversa" in df.columns:
        parsed_dates = pd.to_datetime(df["data_inversa"], errors="coerce")
        invalid_rows.append(
            {
                "coluna": "data_inversa",
                "regra": "data valida",
                "valores_invalidos": int(parsed_dates.isna().sum()),
            }
        )

    if "horario" in df.columns:
        parsed_times = pd.to_datetime(df["horario"], format="%H:%M:%S", errors="coerce")
        invalid_rows.append(
            {
                "coluna": "horario",
                "regra": "hora valida no formato HH:MM:SS",
                "valores_invalidos": int(parsed_times.isna().sum()),
            }
        )

    return {
        "tipos": pd.DataFrame(type_rows),
        "nulos": null_report,
        "invalidos": pd.DataFrame(invalid_rows),
    }
