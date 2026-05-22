"""CSV storage helpers for the Streamlit MVP."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def append_to_csv(file_path: str | Path, row: dict) -> None:
    """Append a single row to a CSV file, creating the file if necessary."""

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    new_row = pd.DataFrame([row])
    if path.exists() and path.stat().st_size > 0:
        existing = pd.read_csv(path)
        combined = pd.concat([existing, new_row], ignore_index=True)
    else:
        combined = new_row

    combined.to_csv(path, index=False)
