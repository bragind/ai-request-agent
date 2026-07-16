from __future__ import annotations

import re

# Нормализация вынесена отдельно, чтобы вход и summary обрабатывались одинаково.

SPACE_RE = re.compile(r"\s+")


def normalize_text(value: str) -> str:
    """Убирает крайние и повторяющиеся пробельные символы из текста."""

    return SPACE_RE.sub(" ", value.strip())
