"""Scoring: exposure-normalized rates -> percentile ranks -> weighted 0-100 scores.

Design principles:
  - Events are normalized per 100 km (never raw counts) so high-mileage
    drivers/vehicles are not penalized for exposure alone.
  - Percentile-rank normalization (robust to outliers, unlike min-max).
  - Weights are a transparent starting framework, documented in METHODOLOGY.md.
"""
import pandas as pd

DRIVER_WEIGHTS = {  # driver behaviour risk
    "speeding_rate": 0.40,
    "harsh_brake_rate": 0.25,
    "harsh_accel_rate": 0.20,
    "impact_rate": 0.10,
    "aggressive_turn_rate": 0.05,
}
VEHICLE_WEIGHTS = {  # maintenance risk
    "vib_score": 0.30,
    "rotation_score": 0.25,
    "service_score": 0.20,
    "age_score": 0.15,
    "usage_score": 0.10,
}

DRIVER_BANDS = [(0, 30, "Low"), (31, 60, "Moderate"), (61, 80, "High"), (81, 100, "Critical")]
VEHICLE_BANDS = [(0, 30, "Healthy"), (31, 60, "Monitor"), (61, 80, "Watch"), (81, 100, "High Risk")]


def _band(score, bands):
    for lo, hi, label in bands:
        if lo <= score <= hi:
            return label
    return bands[-1][2]


def _rates_per_100km(g: pd.DataFrame) -> pd.DataFrame:
    """g must contain event sums and exposure_km."""
    out = pd.DataFrame(index=g.index)
    for e in ["ev_speeding", "ev_harsh_accel", "ev_harsh_brake", "ev_impact", "ev_aggressive_turn"]:
        out[e.replace("ev_", "") + "_rate"] = g[e] / g["exposure_km"] * 100
    return out


def driver_scores(trips_ev: pd.DataFrame, dr: pd.DataFrame) -> pd.DataFrame:
    ev = ["ev_speeding", "ev_harsh_accel", "ev_harsh_brake", "ev_impact", "ev_aggressive_turn"]
    g = trips_ev.groupby("Driver_ID").agg(
        trips=("Trip_ID", "count"),
        total_min=("Duration_Min", "sum"),
        exposure_km=("Distance_KM_Corrected", "sum"),
        max_speed=("Max_Speed_kmph", "max"),
        idle_share=("idle_share", "mean"),
        **{e: (e, "sum") for e in ev},
    )
    rates = _rates_per_100km(g)
    ranks = rates.rank(pct=True) * 100  # percentile rank 0-100
    score = sum(ranks[c] * w for c, w in DRIVER_WEIGHTS.items())

    out = dr.set_index("Driver_ID").join([g, rates.add_suffix("_per100km"), ranks.add_suffix("_pct")])
    out["risk_score"] = score.round(1)
    out["risk_category"] = out["risk_score"].map(lambda s: _band(s, DRIVER_BANDS))
    return out.reset_index()


def vehicle_scores(trips_ev: pd.DataFrame, vh: pd.DataFrame, tl: pd.DataFrame) -> pd.DataFrame:
    ev = ["ev_impact", "ev_aggressive_turn"]
    g = trips_ev.groupby("Vehicle_ID").agg(
        trips=("Trip_ID", "count"),
        n_drivers=("Driver_ID", "nunique"),
        exposure_km=("Distance_KM_Corrected", "sum"),
        vib_p95=("vib_p95", "mean"),
        vib_band_mean=("vib_band_mean", "mean"),
        idle_roughness=("idle_roughness", "mean"),
        **{e: (e, "sum") for e in ev},
    )
    g["impact_rate"] = g["ev_impact"] / g["exposure_km"] * 100
    g["rotation_rate"] = g["ev_aggressive_turn"] / g["exposure_km"] * 100

    comp = pd.DataFrame(index=g.index)
    comp["vib_score"] = (0.5 * g["vib_band_mean"].rank(pct=True)
                         + 0.3 * g["idle_roughness"].rank(pct=True)
                         + 0.2 * g["impact_rate"].rank(pct=True)) * 100
    comp["rotation_score"] = g["rotation_rate"].rank(pct=True) * 100

    v = vh.set_index("Vehicle_ID")
    comp["service_score"] = v["Days_Since_Service"].rank(pct=True) * 100
    comp["age_score"] = v["Vehicle_Age_Years"].rank(pct=True) * 100
    comp["usage_score"] = g["exposure_km"].rank(pct=True) * 100

    score = sum(comp[c] * w for c, w in VEHICLE_WEIGHTS.items())
    out = v.join([g, comp])
    out["est_odometer_km"] = out["Odometer_KM_Start_of_Week"] + out["exposure_km"]
    out["maintenance_risk"] = score.round(1)
    out["health_category"] = out["maintenance_risk"].map(lambda s: _band(s, VEHICLE_BANDS))
    return out.reset_index()
