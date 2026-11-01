import pandas as pd
import pytest
from src.data.validate import validate_frame
from src.data.filters import apply_filters
from src.analytics.metrics import overview_metrics
from src.analytics.clustering import run_kmeans
from src.analytics.association import encode_transactions, run_apriori
from src.ui.exports import safe_csv

def sample():
    return pd.DataFrame([{"Date":f"2024-01-{i%9+1:02d}","Booking Status":"Completed" if i%3 else "Cancelled by Driver","Vehicle Type":"Auto" if i%2 else "Bike","Pickup Location":"A","Drop Location":"B","Avg VTAT":3+i%4,"Avg CTAT":5+i%5,"Booking Value":100+i,"Ride Distance":2+i%7,"Booking ID":"=bad","Customer ID":"CID"} for i in range(30)])

def test_validation_rejects_missing_columns(): assert validate_frame(pd.DataFrame({"Date":["2024-01-01"]})).errors
def test_filters_metrics():
    f=sample(); filtered=apply_filters(f,pd.Timestamp("2024-01-01").date(),pd.Timestamp("2024-01-09").date(),["Auto"],None,None,None); m=overview_metrics(filtered)
    assert m["total"]==15 and m["completed"]==10 and m["completion_rate"]==pytest.approx(2/3)
def test_kmeans_and_association():
    f=sample(); assert run_kmeans(f,2,max_rows=30)["sample_size"]==20
    assert encode_transactions(f).shape[0]==30
    assert not run_apriori(f,.1,.1,1,max_rows=30)[0].empty
def test_export_is_private():
    exported=safe_csv(sample()).decode(); assert "Customer ID" not in exported and "Booking ID" not in exported
