"""Feature engineering: orientation-invariant magnitudes + threshold-based events.

Thresholds (validated against observed distributions, see METHODOLOGY.md):
  SPEEDING_KMPH   = 50   # P99 of speed = 51.3 -> top ~1.3% of readings
  HARSH_DELTA     = 20   # km/h per minute; between P90 (18.5) and P95 (25.4)
  IMPACT_G        = 1.3  # accel magnitude; P99 = 1.43 -> top ~1.4%
  GYRO_DPS        = 20   # gyro magnitude; gated by speed > 25 to exclude
  GYRO_MIN_SPEED  = 25   #   stationary handlebar turns (252 artifacts removed)
"""
import numpy as np
import pandas as pd

SPEEDING_KMPH = 50
HARSH_DELTA = 20
IMPACT_G = 1.3
GYRO_DPS = 20
GYRO_MIN_SPEED = 25
IDLE_SPEED = 3


def add_telemetry_features(tl: pd.DataFrame) -> pd.DataFrame:
    tl = tl.sort_values(["Trip_ID", "Timestamp"]).copy()

    # Orientation-invariant magnitudes (phone mount orientation unknown)
    tl["accel_mag"] = np.sqrt(tl["Accel_X_g"]**2 + tl["Accel_Y_g"]**2 + tl["Accel_Z_g"]**2)
    tl["gyro_mag"] = np.sqrt(tl["Gyro_X_dps"]**2 + tl["Gyro_Y_dps"]**2 + tl["Gyro_Z_dps"]**2)
    tl["accel_dev"] = (tl["accel_mag"] - 1.0).abs()  # deviation from gravity

    # Same-trip speed delta (never across trips)
    tl["speed_delta"] = tl["Speed_kmph"] - tl.groupby("Trip_ID")["Speed_kmph"].shift(1)

    # Event flags
    tl["ev_speeding"] = tl["Speed_kmph"] > SPEEDING_KMPH
    tl["ev_harsh_accel"] = tl["speed_delta"] > HARSH_DELTA
    tl["ev_harsh_brake"] = tl["speed_delta"] < -HARSH_DELTA
    tl["ev_impact"] = tl["accel_mag"] > IMPACT_G
    tl["ev_aggressive_turn"] = (tl["gyro_mag"] > GYRO_DPS) & (tl["Speed_kmph"] > GYRO_MIN_SPEED)
    tl["is_idle"] = tl["Speed_kmph"] < IDLE_SPEED
    return tl


def trip_level(tl: pd.DataFrame, tr: pd.DataFrame) -> pd.DataFrame:
    """Aggregate telemetry events to trip level and join trip metadata."""
    ev = ["ev_speeding", "ev_harsh_accel", "ev_harsh_brake", "ev_impact", "ev_aggressive_turn"]
    agg = tl.groupby("Trip_ID").agg(
        n_readings=("Speed_kmph", "size"),
        **{e: (e, "sum") for e in ev},
        idle_min=("is_idle", "sum"),
        vib_p95=("accel_dev", lambda s: s.quantile(0.95)),
    )
    # Speed-band-controlled vibration: 20-40 km/h band (controls for road/speed mix)
    band = tl[tl["Speed_kmph"].between(20, 40)]
    band_vib = band.groupby("Trip_ID")["accel_dev"].mean().rename("vib_band_mean")
    # Idle roughness: accel deviation while stationary
    idle_vib = tl[tl["is_idle"]].groupby("Trip_ID")["accel_dev"].std().rename("idle_roughness")

    t = tr.set_index("Trip_ID").join([agg, band_vib, idle_vib]).reset_index()
    t["idle_share"] = t["idle_min"] / t["n_readings"]
    return t
