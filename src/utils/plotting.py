from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns


DARK_THEME_CONFIG = {
    "axes.facecolor": "#1e1e1e",
    "figure.facecolor": "#121212",
    "grid.color": "#333333",
    "axes.edgecolor": "#333333",
    "text.color": "white",
    "axes.labelcolor": "white",
    "xtick.color": "white",
    "ytick.color": "white",
}


def apply_dark_theme() -> None:
    """Aplica o estilo visual usado em todos os graficos do trabalho."""
    plt.style.use("dark_background")
    sns.set_theme(style="darkgrid", rc=DARK_THEME_CONFIG)


def save_report_figure(reports_dir: str | Path, file_name: str, dpi: int = 300) -> Path:
    """Salva a figura atual na pasta de relatorios e retorna o caminho gerado."""
    output_path = Path(reports_dir) / file_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi)
    return output_path
