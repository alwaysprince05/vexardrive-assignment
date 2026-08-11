"""Build pipeline: raw xlsx -> enriched parquet tables in data/."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from data_prep import load_all
from features import add_telemetry_features, trip_level
from scoring import driver_scores, vehicle_scores

OUT = Path("data")
OUT.mkdir(exist_ok=True)

dr, vh, tr, tl = load_all()
tl = add_telemetry_features(tl)
trips_ev = trip_level(tl, tr)
dscores = driver_scores(trips_ev, dr)
vscores = vehicle_scores(trips_ev, vh, tl)

tl.to_parquet(OUT / "telemetry.parquet", index=False)
trips_ev.to_parquet(OUT / "trips.parquet", index=False)
dscores.to_parquet(OUT / "driver_scores.parquet", index=False)
vscores.to_parquet(OUT / "vehicle_scores.parquet", index=False)
dr.to_parquet(OUT / "drivers.parquet", index=False)
vh.to_parquet(OUT / "vehicles.parquet", index=False)

# ---- QA reconciliation ----
print("=== QA ===")
print("driver exposure sum:", round(dscores["exposure_km"].sum(), 2),
      "| trip corrected sum:", round(trips_ev["Distance_KM_Corrected"].sum(), 2),
      "| vehicle exposure sum:", round(vscores["exposure_km"].sum(), 2))
print("driver score range:", dscores["risk_score"].min(), "-", dscores["risk_score"].max())
print("vehicle score range:", vscores["maintenance_risk"].min(), "-", vscores["maintenance_risk"].max())
print("distance flagged inconsistent:", (trips_ev["Distance_Flag"] == "inconsistent").sum(), "of", len(trips_ev))

print("\n=== Top 8 riskiest drivers ===")
cols = ["Driver_ID", "Driver_Name", "trips", "exposure_km", "max_speed",
        "speeding_rate_per100km", "harsh_brake_rate_per100km", "risk_score", "risk_category"]
print(dscores.sort_values("risk_score", ascending=False)[cols].head(8).round(2).to_string(index=False))

print("\n=== Top 8 maintenance-risk vehicles ===")
vcols = ["Vehicle_ID", "Make", "Model", "Vehicle_Age_Years", "Days_Since_Service",
         "n_drivers", "exposure_km", "vib_band_mean", "maintenance_risk", "health_category"]
print(vscores.sort_values("maintenance_risk", ascending=False)[vcols].head(8).round(3).to_string(index=False))

print("\n=== Vehicle-swap check (vehicles used by >1 driver) ===")
sw = vscores[vscores["n_drivers"] > 1][["Vehicle_ID", "n_drivers", "maintenance_risk"]]
print(sw.sort_values("n_drivers", ascending=False).to_string(index=False))
