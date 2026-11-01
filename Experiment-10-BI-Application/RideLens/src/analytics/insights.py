from src.analytics.metrics import overview_metrics
from src.config import STATUS, VEHICLE
def generate_insights(frame):
    m=overview_metrics(frame)
    if not m['total']: return ["No observations match the active filters."]
    lines=[f"Completed bookings account for {m['completed']:,} of {m['total']:,} visible records ({m['completion_rate']:.1%})."]
    if m['cancelled']: lines.append(f"Driver, customer, and no-driver outcomes total {m['cancelled']:,} records ({m['cancellation_rate']:.1%}); this is descriptive, not causal.")
    vehicle=frame.groupby(VEHICLE).size().sort_values(ascending=False)
    if len(vehicle): lines.append(f"{vehicle.index[0]} has the largest visible volume ({vehicle.iloc[0]:,} records).")
    return lines
