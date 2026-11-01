from __future__ import annotations
import pandas as pd
from src.config import DATE, STATUS, VEHICLE, PICKUP, DROP

def apply_filters(frame: pd.DataFrame, start=None, end=None, vehicles=None, statuses=None, pickups=None, drops=None) -> pd.DataFrame:
    data = frame.copy()
    # Accept canonical frames and simple test/user frames; invalid dates simply do not match.
    dates = pd.to_datetime(data[DATE], errors="coerce")
    if start is not None: data = data[dates.dt.date >= start]
    if end is not None: data = data[dates.dt.date <= end]
    for col, choices in ((VEHICLE, vehicles), (STATUS, statuses), (PICKUP, pickups), (DROP, drops)):
        if choices: data = data[data[col].isin(choices)]
    return data
