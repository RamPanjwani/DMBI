from __future__ import annotations
from dataclasses import dataclass, field
import pandas as pd
from src.config import DATE, REQUIRED_COLUMNS

@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    rows: int = 0
    duplicates: int = 0
    invalid_dates: int = 0

def validate_frame(frame: pd.DataFrame) -> ValidationReport:
    report = ValidationReport(rows=len(frame))
    cols = {str(c).strip() for c in frame.columns}
    missing = sorted(REQUIRED_COLUMNS - cols)
    if missing:
        report.errors.append("Missing required columns: " + ", ".join(missing) + ".")
        return report
    if frame.empty:
        report.errors.append("The CSV contains no booking rows.")
        return report
    dates = pd.to_datetime(frame[DATE], errors="coerce")
    report.invalid_dates = int(dates.isna().sum())
    report.duplicates = int(frame.duplicated().sum())
    if report.invalid_dates:
        report.warnings.append(f"{report.invalid_dates:,} rows have an invalid or missing date and are excluded from date filters.")
    if report.duplicates:
        report.warnings.append(f"{report.duplicates:,} exact duplicate rows detected; rows are retained.")
    return report
