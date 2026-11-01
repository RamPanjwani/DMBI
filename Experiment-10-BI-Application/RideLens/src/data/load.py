"""Safe local CSV loading and canonical type conversion."""
from __future__ import annotations
import hashlib
from pathlib import Path
from typing import BinaryIO
import pandas as pd
from src.config import DATE, NUMERIC_COLUMNS
from src.data.validate import ValidationReport, validate_frame

MAX_UPLOAD_BYTES = 50 * 1024 * 1024

def _clean_frame(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result.columns = [str(c).strip() for c in result.columns]
    result[DATE] = pd.to_datetime(result[DATE], errors="coerce")
    for col in NUMERIC_COLUMNS:
        if col in result:
            result[col] = pd.to_numeric(result[col], errors="coerce")
    for col in result.select_dtypes(include="object"):
        result[col] = result[col].str.strip()
    return result

def read_csv(source: str | Path | BinaryIO) -> tuple[pd.DataFrame, ValidationReport]:
    try:
        frame = pd.read_csv(source, low_memory=False)
    except (UnicodeDecodeError, pd.errors.ParserError, OSError) as exc:
        raise ValueError(f"Could not read this CSV: {exc}") from exc
    report = validate_frame(frame)
    if report.errors:
        raise ValueError(" ".join(report.errors))
    return _clean_frame(frame), report

def file_fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()[:12]
