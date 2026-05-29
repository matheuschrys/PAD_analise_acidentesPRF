from __future__ import annotations

import pandas as pd


def add_period_columns(df: pd.DataFrame, date_column: str = "data_inversa") -> pd.DataFrame:
    """Adiciona colunas de ano, trimestre e semestre usando a coluna de data informada."""
    result = df.copy()
    dates = pd.to_datetime(result[date_column], errors="coerce")

    result["ano"] = dates.dt.year.astype("Int64")
    result["trimestre"] = dates.dt.quarter.astype("Int64")
    result["semestre"] = (((dates.dt.month - 1) // 6) + 1).astype("Int64")
    result["ano_trimestre"] = result["ano"].astype(str) + "-T" + result["trimestre"].astype(str)
    result["ano_semestre"] = result["ano"].astype(str) + "-S" + result["semestre"].astype(str)

    invalid_mask = dates.isna()
    result.loc[invalid_mask, ["ano_trimestre", "ano_semestre"]] = pd.NA
    return result


def filter_by_quarter(df: pd.DataFrame, year: int, quarter: int, date_column: str = "data_inversa") -> pd.DataFrame:
    """Filtra o DataFrame por ano e trimestre calendario."""
    if quarter not in {1, 2, 3, 4}:
        raise ValueError("quarter deve ser um valor entre 1 e 4")

    with_periods = add_period_columns(df, date_column=date_column)
    return with_periods[(with_periods["ano"] == year) & (with_periods["trimestre"] == quarter)].copy()


def filter_by_semester(df: pd.DataFrame, year: int, semester: int, date_column: str = "data_inversa") -> pd.DataFrame:
    """Filtra o DataFrame por ano e semestre calendario."""
    if semester not in {1, 2}:
        raise ValueError("semester deve ser 1 ou 2")

    with_periods = add_period_columns(df, date_column=date_column)
    return with_periods[(with_periods["ano"] == year) & (with_periods["semestre"] == semester)].copy()


def summarize_by_period(
    df: pd.DataFrame,
    period_column: str,
    accident_id_column: str = "id",
    victim_columns: tuple[str, ...] = ("mortos", "feridos_graves", "feridos_leves"),
) -> pd.DataFrame:
    """Resume acidentes unicos e vitimas por uma coluna de periodo ja criada."""
    aggregations = {"acidentes": (accident_id_column, "nunique")}
    for column in victim_columns:
        if column in df.columns:
            aggregations[column] = (column, "sum")

    return (
        df.dropna(subset=[period_column])
        .groupby(period_column, observed=True)
        .agg(**aggregations)
        .reset_index()
        .sort_values(period_column)
    )
