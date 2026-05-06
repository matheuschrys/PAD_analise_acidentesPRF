from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any


def measure_seconds(function: Callable[[], Any]) -> tuple[Any, float]:
    """Executa uma funcao e retorna seu resultado com a duracao em segundos."""
    start = time.time()
    result = function()
    duration = round(time.time() - start, 4)
    return result, duration
