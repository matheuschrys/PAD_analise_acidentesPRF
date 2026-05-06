from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

import pandas as pd


def measure_seconds(function: Callable[[], Any]) -> tuple[Any, float]:
    """Executa uma funcao e retorna seu resultado com a duracao em segundos."""
    start = time.time()
    result = function()
    duration = round(time.time() - start, 4)
    return result, duration


def format_bytes(size_bytes: int | float) -> str:
    """Formata bytes em uma unidade legivel para relatorios."""
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(size) < 1024 or unit == "TB":
            return f"{size:.2f} {unit}"
        size /= 1024


def directory_size_bytes(path: str | Path) -> int:
    """Soma o tamanho dos arquivos dentro de uma pasta ou retorna o tamanho de um arquivo."""
    path = Path(path)
    if path.is_file():
        return path.stat().st_size
    if not path.exists():
        return 0
    return sum(file.stat().st_size for file in path.rglob("*") if file.is_file())


def conversion_size_report(csv_paths: Iterable[str | Path], parquet_dir: str | Path) -> pd.DataFrame:
    """Compara o tamanho dos CSVs originais com os Parquets gerados por ano."""
    parquet_dir = Path(parquet_dir)
    rows = []

    for csv_path in csv_paths:
        csv_path = Path(csv_path)
        year = "".join(character for character in csv_path.stem if character.isdigit())[:4]
        parquet_path = parquet_dir / f"acidentes_{year}.parquet"

        csv_size = csv_path.stat().st_size if csv_path.exists() else 0
        parquet_size = parquet_path.stat().st_size if parquet_path.exists() else 0
        reduction_percent = 0 if csv_size == 0 else (1 - parquet_size / csv_size) * 100

        rows.append(
            {
                "ano": year,
                "arquivo_csv": csv_path.name,
                "arquivo_parquet": parquet_path.name,
                "csv_bytes": csv_size,
                "parquet_bytes": parquet_size,
                "csv_tamanho": format_bytes(csv_size),
                "parquet_tamanho": format_bytes(parquet_size),
                "csv_mb": round(csv_size / 1024**2, 2),
                "parquet_mb": round(parquet_size / 1024**2, 2),
                "reducao_percentual": round(reduction_percent, 2),
            }
        )

    return pd.DataFrame(rows)
