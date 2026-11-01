from __future__ import annotations
import pandas as pd
from src.config import STATUS, COMPLETED, CANCEL_STATUSES

def safe_rate(numerator: int | float, denominator: int | float) -> float | None:
    return None if not denominator else float(numerator) / float(denominator)

def overview_metrics(frame: pd.DataFrame) -> dict:
    total = len(frame); completed = int((frame[STATUS] == COMPLETED).sum())
    cancelled = int(frame[STATUS].isin(CANCEL_STATUSES).sum())
    rides = frame.loc[frame[STATUS].eq(COMPLETED)]
    values = pd.to_numeric(rides.get("Booking Value"), errors="coerce")
    dist = pd.to_numeric(rides.get("Ride Distance"), errors="coerce")
    return {"total": total, "completed": completed, "completion_rate": safe_rate(completed,total), "cancelled":cancelled,
      "cancellation_rate":safe_rate(cancelled,total), "completed_value":float(values.sum(min_count=1)) if values.notna().any() else None,
      "average_value":float(values.mean()) if values.notna().any() else None, "mean_distance":float(dist.mean()) if dist.notna().any() else None,
      "driver_cancelled":int((frame[STATUS]=="Cancelled by Driver").sum()), "customer_cancelled":int((frame[STATUS]=="Cancelled by Customer").sum()), "no_driver":int((frame[STATUS]=="No Driver Found").sum())}

def grouped_counts(frame: pd.DataFrame, column: str, top: int | None=None) -> pd.DataFrame:
    out = frame.groupby(column, dropna=False).size().rename("Bookings").reset_index().sort_values("Bookings", ascending=False)
    return out.head(top) if top else out
