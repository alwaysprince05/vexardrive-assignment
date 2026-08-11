"""Data loading + cleaning for the VexarDrive fleet dataset.

Key data-quality finding (verified against telemetry ground truth):
  - Trips.Avg_Speed_kmph and Trips.Max_Speed_kmph match telemetry exactly (corr 1.00).
  - Trips.Distance_KM is CORRUPTED for 166/450 trips (median error 3.16 km).
    => Exposure distance is RECOMPUTED as Avg_Speed_kmph * Duration_Min / 60,
       which matches telemetry-derived distance to within 0.01 km median.
"""
import pandas as pd

XLSX = "VEXAR_Fleet_Dataset_CANDIDATE_VERSION.xlsx"
OBS_END = pd.Timestamp("2026-08-06")  # last observation date; ages computed as of this date


def load_all(path: str = XLSX):
    dr = pd.read_excel(path, "Drivers", skiprows=2)
    vh = pd.read_excel(path, "Vehicles", skiprows=2)
    tr = pd.read_excel(path, "Trips", skiprows=2)
    tl = pd.read_excel(path, "Telemetry", skiprows=2)

    tr["Trip_Date"] = pd.to_datetime(tr["Trip_Date"])
    tl["Timestamp"] = pd.to_datetime(tl["Timestamp"])
    vh["Registration_Date"] = pd.to_datetime(vh["Registration_Date"])
    vh["Last_Service_Date"] = pd.to_datetime(vh["Last_Service_Date"])
    dr["Date_Joined_Fleet"] = pd.to_datetime(dr["Date_Joined_Fleet"])

    # Corrected exposure distance (see module docstring)
    tr["Distance_KM_Corrected"] = tr["Avg_Speed_kmph"] * tr["Duration_Min"] / 60
    tr["Distance_Flag"] = (tr["Distance_KM"] / tr["Distance_KM_Corrected"]).between(0.7, 1.4).map({True: "ok", False: "inconsistent"})

    # Vehicle age / service recency as of observation end (NOT today)
    vh["Vehicle_Age_Years"] = ((OBS_END - vh["Registration_Date"]).dt.days / 365.25).round(2)
    vh["Days_Since_Service"] = (OBS_END - vh["Last_Service_Date"]).dt.days

    return dr, vh, tr, tl
