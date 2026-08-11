# VexarDrive Technologies — Fleet Data Science & Analytics Submission

**Candidate**: Data Science Intern Candidate  
**Target Organization**: VexarDrive Technologies x Polaris  
**Dataset Overview**: 30 Drivers | 30 Vehicles | 450 Trips | 12,987 Telemetry Logs (1 Week)  
**Submission Date**: August 2026  

---

## 1. Executive Summary

This project delivers an end-to-end telemetry analytics solution and interactive dashboard application for VexarDrive's two-wheeler delivery fleet. By processing per-minute GPS and IMU (accelerometer + gyroscope) mobile sensor feeds, we built two core diagnostic systems:

1. **Driver Behaviour & Safety Risk Engine**: Scores drivers on a 0–100 risk scale by evaluating exposure-normalized speeding, harsh braking, aggressive acceleration, impacts, and cornering.
2. **Vehicle Health & Predictive Maintenance Engine**: Identifies vehicles exhibiting mechanical degradation by isolating engine idle roughness, chassis vibration in normalized speed bands, gyro instabilities, and service recency.

---

## 2. Key Analytical & Data Quality Insights

### 2.1 Critical Data Quality Finding: Distance Corruption
During initial exploratory data analysis, **166 out of 450 trips (~36.9%)** in the `Trips` table exhibited severe distance corruption (e.g. static distances or mismatched odometer increments). 

- **Verification**: Cross-referencing `Avg_Speed_kmph` and `Duration_Min` against high-frequency telemetry timestamps revealed a **1.00 correlation**.
- **Resolution**: We re-derived trip distance using kinematic integration:
  $$\text{Distance\_KM\_Corrected} = \frac{\text{Avg\_Speed\_kmph} \times \text{Duration\_Min}}{60}$$
  This eliminated exposure estimation bias across high-mileage delivery routes.

### 2.2 Orientation-Invariant Sensor Fusion
Because mobile devices are mounted at arbitrary angles on two-wheeler handlebars, individual $X, Y, Z$ axial acceleration/gyroscope values are unreliable. We transformed raw readings into **orientation-invariant vector magnitudes** and deviation from standard gravity ($1.0g$).

### 2.3 Noise Reduction: Speed-Gated Gyroscope Filtering
Stationary drivers turning handlebars while parked generated artificial gyroscope spikes ($>20\text{ deg/s}$). Gating gyroscope metrics with a speed threshold ($\text{Speed} > 25\text{ km/h}$) eliminated **252 false-positive turning events**.

---

## 3. Fleet Risk Landscape & Key Findings

### 3.1 Driver Safety Profile
- **Total Fleet Distance (Corrected)**: 5,234.7 km across 450 trips.
- **Top Critical-Risk Drivers**:
  - **D23 (Kavya Pillai)**: Risk Score **96.8** (Critical) — 14.1 speeding events / 100 km, 42.3 harsh brakes / 100 km, max speed 70.2 km/h.
  - **D14 (Rajesh Subramaniam)**: Risk Score **90.2** (Critical) — 13.3 speeding events / 100 km, 41.0 harsh brakes / 100 km.
  - **D24 (Lakshmi Iyer)**: Risk Score **89.7** (Critical) — 13.2 speeding events / 100 km, 42.2 harsh brakes / 100 km.

### 3.2 Vehicle Health & Maintenance Profile
- **Top Maintenance-Risk Vehicles**:
  - **V19 (TVS Ntorq)**: Maintenance Risk **78.7** (Watch) — 48 days since service, high vibration ($0.084g$ in 20-40 km/h band), operated by 2 different drivers.
  - **V12 (TVS Ntorq)**: Maintenance Risk **76.8** (Watch) — 58 days since service, age 6.3 years.
  - **V01 (Yamaha Ray ZR)**: Maintenance Risk **76.6** (Watch) — 59 days since service, age 5.3 years.
- **Cross-Driver Validation (Vehicle Swap Analysis)**:
  For multi-driver vehicles such as **V23** (driven by 4 different drivers, risk score **76.2**) and **V19** (driven by 2 drivers, risk score **78.7**), high vibration persisted across all drivers. This proves that vibration is an **intrinsic vehicle mechanical issue** (e.g. worn suspension / engine mounts) rather than driver handling style.

---

## 4. Strategic Proposals: Beyond the Two Dashboards

Beyond driver scoring and vehicle maintenance tracking, this rich smartphone telemetry dataset enables several high-value business use cases for VexarDrive:

### 1. Dynamic Telematics-Based Insurance & Claims Automation
- **Usage-Based Insurance (UBI)**: Transition fleet insurance from flat rates to pay-how-you-drive models. Low-risk drivers (Score < 30) can receive premium discounts, directly reducing fleet operational expenditure.
- **Automated Accident Detection & Reconstruction**: Instant alert generation when $\text{accel\_mag} > 2.5g$ combined with sudden speed drop. Pre-impact telemetry (speed, tilt, braking) can automate insurance claim processing and dispatch emergency response.

### 2. Road Quality & Infrastructure Mapping (Pothole Sensing)
- **Crowdsourced Pothole & Road Bump Indexing**: By isolating high accelerometer impacts ($\text{accel\_mag} > 1.3g$) that recur across multiple drivers at exact GPS coordinates, VexarDrive can create a live road-quality heatmap.
- **Dynamic Route Optimization**: Reroute two-wheelers around severely degraded roads to protect cargo, reduce vehicle wear, and prevent accidents.

### 3. Driver Fatigue & Shift Safety Optimization
- **Intra-Shift Risk Acceleration**: Analyze how risk scores change from Trip 1 to Trip 15 within a single day. Increased harsh braking and speeding in later hours indicates driver fatigue.
- **Smart Shift Scheduling**: Implement mandatory rest intervals or cap daily trip counts when fatigue markers spike.

### 4. Carbon Footprint & Eco-Driving Optimization
- **Fuel Inefficiency Score**: Calculate fuel wastage caused by excessive idling (speed < 3 km/h with engine on) and aggressive throttle changes.
- **Eco-Driving Coaching**: Provide targeted feedback to drivers to reduce CO2 emissions and lower fuel/charging costs.

---

## 5. Dashboard Implementation & Instructions

The accompanying Streamlit dashboard provides an interactive overview of the entire dataset.

- **To run locally**:
  ```bash
  .venv/bin/streamlit run app.py
  ```
- **Structure**:
  - `app.py`: Multi-page web dashboard (Executive Overview, Driver Safety, Vehicle Health, Methodology).
  - `src/data_prep.py`: Data ingestion & distance correction.
  - `src/features.py`: Orientation-invariant signal processing & event detection.
  - `src/scoring.py`: Percentile-rank weighted scoring engine.
  - `src/build.py`: Pipeline executor generating parquet outputs in `data/`.
