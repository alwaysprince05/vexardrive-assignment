# VexarDrive Fleet Analytics & Telemetry Dashboard

[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)

This repository contains the complete candidate solution for the **VexarDrive Technologies x Polaris Data Scientist Intern Assignment**.

---

## 📌 Quick Start

### 1. Prerequisites & Environment Setup
Ensure you have Python 3.10+ installed.

```bash
# Clone the repository and navigate to folder
cd vexardrive-assignment

# Activate virtual environment (if present) or create one
python3 -m venv .venv
source .venv/bin/activate

# Install required dependencies
pip install pandas numpy openpyxl plotly streamlit pyarrow
```

### 2. Run Data Pipeline (ETL & Scoring)
To re-process raw Excel data, execute data cleaning, re-derive corrected trip distances, compute telemetry features, and output clean Parquet tables:

```bash
python src/build.py
```

### 3. Launch Interactive Streamlit Dashboard
To launch the 4-page interactive web application:

```bash
streamlit run app.py
```
Or with `.venv`:
```bash
.venv/bin/streamlit run app.py
```

The dashboard will open automatically at `http://localhost:8501`.

---

## 📂 Repository Layout

```
vexardrive-assignment/
├── VEXAR_Fleet_Dataset_CANDIDATE_VERSION.xlsx  # Raw candidate dataset
├── app.py                                       # Streamlit multi-page dashboard
├── METHODOLOGY.md                               # Mathematical formulas, feature definitions, & assumptions
├── EXECUTIVE_REPORT.md                          # Full candidate evaluation report & strategic proposals
├── README.md                                    # Project documentation & setup instructions
├── src/
│   ├── data_prep.py                             # Data cleaning & distance correction logic
│   ├── features.py                              # Orientation-invariant magnitudes & event detection
│   ├── scoring.py                               # Percentile-rank driver & vehicle scoring engines
│   └── build.py                                 # ETL pipeline executor
└── data/                                        # Generated parquet tables
    ├── driver_scores.parquet
    ├── vehicle_scores.parquet
    ├── trips.parquet
    ├── telemetry.parquet
    ├── drivers.parquet
    └── vehicles.parquet
```

---

## 📊 Summary of Dashboards & Features

1. **Executive Overview**: High-level KPIs (drivers, vehicles, trips, distance), risk category breakdown, risk vs. exposure scatter plot.
2. **Driver Behaviour & Safety**: Interactive driver risk ranking, stacked percentile component contribution (speeding, harsh braking/accel, impact, turning), speed distribution histograms, detailed driver table.
3. **Vehicle Health & Maintenance**: Maintenance risk ranking, vibration vs. vehicle age scatter plot, **cross-driver vehicle-swap analysis** (isolating vehicle defects from driver behavior), vehicle detail table.
4. **Methodology & Data Quality**: Full breakdown of data quality checks (distance anomaly correction), event thresholds, scoring formulas, and key assumptions.
