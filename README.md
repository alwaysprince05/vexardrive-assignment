# VexarDrive Fleet Analytics & Telemetry Diagnostics Engine

[![Live App](https://img.shields.io/badge/🚀%20Live%20App-View%20Live%20App-00E676?style=for-the-badge&logo=streamlit)](https://vexardrive-assignment.streamlit.app)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.61%2B-FF4B4B?style=for-the-badge&logo=streamlit)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

Candidate Evaluation Solution for **VexarDrive Technologies × Polaris** Data Science Intern Assignment.

---

## 🌐 Live Interactive Dashboard

Access the deployed executive dashboard live on any browser:

👉 **[View Live App](https://vexardrive-assignment.streamlit.app)** | 🚀 **[Live Deployed App Link](https://vexardrive-assignment.streamlit.app)**

---

## 📌 Executive Summary & Key Highlights

This repository delivers an end-to-end data processing pipeline, statistical scoring engine, and interactive executive dashboard analyzing 30 drivers, 30 vehicles, 450 trips, and 12,987 per-minute telematics readings.

### 🔍 Key Technical Accomplishments:
1. **Kinematic Distance Reconciliation**: Identified a 36.9% anomaly in raw trip distances (166 corrupt records). Re-derived exact exposure distance using kinematic trapezoidal integration ($\text{Avg\_Speed} \times \text{Duration} / 60$), matching per-minute telemetry logs to **0.01 km precision**.
2. **Orientation-Invariant Feature Engineering**: Calculated 3D vector magnitudes ($\text{accel\_mag}$, $\text{gyro\_mag}$, $\text{accel\_dev}$) to handle arbitrary smartphone mounting angles on delivery two-wheelers.
3. **Speed-Gated Gyroscope Noise Filtering**: Applied speed gating ($\text{Speed} > 25\text{ km/h}$) to eliminate **252 false stationary handlebar turn artifacts**.
4. **Dual Risk Engines**: Formulated 0–100 percentile-rank scoring engines for Driver Safety (40% Speeding, 25% Harsh Braking, 20% Harsh Accel, 10% Impact, 5% Turn) and Vehicle Maintenance Health.
5. **Cross-Driver Vehicle Swap Validation**: Isolated intrinsic mechanical faults (suspension/engine mount wear) from driver style using multi-driver vehicle swap analysis on shared vehicles (`V23`, `V19`, `V02`).

---

## 💻 Quick Start & Local Execution

### 1. Installation & Environment Setup

```bash
# Clone the repository
git clone git@github.com:alwaysprince05/vexardrive-assignment.git
cd vexardrive-assignment

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Data Pipeline (ETL & Feature Building)

To execute data cleaning, re-derive trip distances, calculate telematics features, and output Parquet datasets:

```bash
python src/build.py
```

### 3. Launch Interactive Streamlit Dashboard Locally

```bash
streamlit run app.py
```

The app will launch at `http://localhost:8501`.

---

## 📂 Repository Architecture

```
vexardrive-assignment/
├── app.py                                       # Executive Streamlit multi-page dashboard
├── VEXAR_Fleet_Dataset_CANDIDATE_VERSION.xlsx  # Raw candidate dataset
├── EXECUTIVE_REPORT.md                          # Written candidate report & strategic proposals
├── METHODOLOGY.md                               # Mathematical formulas, thresholds & data audit
├── README.md                                    # Project documentation & setup instructions
├── requirements.txt                             # Project dependencies
├── src/
│   ├── data_prep.py                             # Data cleaning & kinematic distance logic
│   ├── features.py                              # Orientation-invariant magnitudes & thresholds
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

## 📑 Core Dashboard Modules

- **Executive Overview**: High-level KPI metric cards, driver risk category distribution, vehicle maintenance health breakdown, and 2D driver risk vs. exposure scatter plot.
- **Driver Behaviour & Safety**: Risk ranking (0-100), stacked component contribution breakdown, speed distribution histogram, individual driver telematics inspector, and driver master table.
- **Vehicle Health & Maintenance**: Maintenance risk ranking, chassis vibration ($20\text{--}40$ km/h band) vs. age scatter plot, **cross-driver vehicle swap analysis**, individual vehicle inspector, and vehicle master table.
- **Methodology & Data Quality**: Interactive mathematical documentation, event threshold justifications, operational assumptions, strategic business proposals, and embedded report reader.

---

## 📄 License & Candidate Information

- **Candidate**: Prince Maurya
- **Target Role**: Data Science Intern — VexarDrive Technologies × Polaris
- **Repository**: [github.com/alwaysprince05/vexardrive-assignment](https://github.com/alwaysprince05/vexardrive-assignment)
- **Live Dashboard**: [👉 View Live App](https://vexardrive-assignment.streamlit.app)
