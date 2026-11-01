from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / "data" / "raw" / "ncr_ride_bookings.csv"
DATE = "Date"
STATUS = "Booking Status"
VEHICLE = "Vehicle Type"
PICKUP = "Pickup Location"
DROP = "Drop Location"
COMPLETED = "Completed"
CANCEL_STATUSES = ("Cancelled by Driver", "Cancelled by Customer", "No Driver Found")
REQUIRED_COLUMNS = {DATE, STATUS, VEHICLE, PICKUP, DROP}
NUMERIC_COLUMNS = ["Avg VTAT", "Avg CTAT", "Booking Value", "Ride Distance", "Driver Ratings", "Customer Rating"]
IDENTIFIER_COLUMNS = {"Booking ID", "Customer ID"}
CLUSTER_FEATURES = ["Avg VTAT", "Avg CTAT", "Booking Value", "Ride Distance"]
ASSOCIATION_COLUMNS = [VEHICLE, PICKUP, DROP, STATUS]
