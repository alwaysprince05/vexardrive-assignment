# VexarDrive Fleet Analytics — Methodology & Scoring Framework

## 1. Data Quality & Pre-Processing Findings

### 1.1 Distance Anomaly Correction
- **Finding**: Out of 450 trips in `Trips.xlsx`, 166 trips (~36.9%) exhibited a severe discrepancy between `Distance_KM` and the per-minute `Telemetry` readings (median discrepancy: 3.16 km).
- **Validation**: `Avg_Speed_kmph` and `Max_Speed_kmph` in `Trips` matched the telemetry summary statistics with a correlation of **1.00**.
- **Action**: Corrected trip exposure distance was recomputed as:
  $$\text{Distance\_KM\_Corrected} = \frac{\text{Avg\_Speed\_kmph} \times \text{Duration\_Min}}{60}$$
  This corrected distance matches telemetry-derived trapezoidal integration to within **0.01 km median error**.

### 1.2 Phone Mount Orientation Invariance
- **Finding**: Drivers mount their mobile phones in varying orientations on two-wheelers (portrait, landscape, tilted).
- **Action**: Raw 3-axis accelerometer $(a_x, a_y, a_z)$ and gyroscope $(g_x, g_y, g_z)$ readings were transformed into **orientation-invariant vector magnitudes**:
  $$\text{accel\_mag} = \sqrt{a_x^2 + a_y^2 + a_z^2}$$
  $$\text{gyro\_mag} = \sqrt{g_x^2 + g_y^2 + g_z^2}$$
  $$\text{accel\_dev} = |\text{accel\_mag} - 1.0g|$$

### 1.3 Stationary Handlebar Artifact Filtering
- **Finding**: Telemetry showed high gyroscope rotation values when vehicles were stationary (e.g., driver turning handlebars while parked).
- **Action**: Aggressive turning events were gated by speed: `(gyro_mag > 20 dps) & (Speed_kmph > 25 km/h)`. This filtered out 252 stationary artifacts.

---

## 2. Event Thresholds & Distribution Basis

| Event | Threshold | Statistical Basis |
|---|---|---|
| **Speeding** | $> 50\text{ km/h}$ | 99th percentile of speed distribution ($P_{99} = 51.3\text{ km/h}$) |
| **Harsh Acceleration** | $> +20\text{ km/h per min}$ | Derived between $P_{90}$ ($18.5$) and $P_{95}$ ($25.4$) speed deltas |
| **Harsh Braking** | $< -20\text{ km/h per min}$ | Derived between $P_{90}$ and $P_{95}$ speed deltas |
| **Impact / Severe Bump** | $\text{accel\_mag} > 1.3g$ | $P_{99}$ accelerometer magnitude ($P_{99} = 1.43g$) |
| **Aggressive Turn** | $\text{gyro\_mag} > 20\text{ dps}$ AND $\text{Speed} > 25\text{ km/h}$ | $P_{95}$ gyroscope reading with speed gating |

---

## 3. Scoring Architecture

### 3.1 Exposure Normalization
All event counts are normalized per **100 km driven** rather than raw counts:
$$\text{Event Rate} = \frac{\sum \text{Events}}{\text{Total Distance (km)}} \times 100$$
This ensures high-mileage drivers/vehicles are not unfairly penalized for higher exposure.

### 3.2 Percentile-Rank Transformation
Raw rates are mapped to a 0–100 percentile rank within the fleet:
$$\text{Percentile Rank} = \text{rank}_{\text{pct}}(\text{Rate}) \times 100$$
Percentile ranking is robust against extreme outliers and provides relative fleet benchmarks.

### 3.3 Driver Risk Score (0 - 100)
$$\text{Driver Risk} = 0.40 \cdot \text{Speeding}_{\text{pct}} + 0.25 \cdot \text{Harsh Brake}_{\text{pct}} + 0.20 \cdot \text{Harsh Accel}_{\text{pct}} + 0.10 \cdot \text{Impact}_{\text{pct}} + 0.05 \cdot \text{Turn}_{\text{pct}}$$

| Risk Category | Score Range | Definition |
|---|---|---|
| **Low** | 0 – 30 | Exemplary safe driving patterns |
| **Moderate** | 31 – 60 | Standard fleet operation |
| **High** | 61 – 80 | Frequent speed/braking violations |
| **Critical** | 81 – 100 | Severe safety risk requiring intervention |

### 3.4 Vehicle Maintenance Risk Score (0 - 100)
$$\text{Vehicle Risk} = 0.30 \cdot \text{Vibration}_{\text{score}} + 0.25 \cdot \text{Rotation}_{\text{score}} + 0.20 \cdot \text{Service Recency}_{\text{score}} + 0.15 \cdot \text{Age}_{\text{score}} + 0.10 \cdot \text{Usage}_{\text{score}}$$

- **Vibration Score**: Evaluated in the $20\text{--}40\text{ km/h}$ speed band to control for road speed variation:
  $$\text{Vibration}_{\text{score}} = 0.50 \cdot \text{Band Vib}_{\text{pct}} + 0.30 \cdot \text{Idle Roughness}_{\text{pct}} + 0.20 \cdot \text{Impact Rate}_{\text{pct}}$$

- **Cross-Driver Validation (Vehicle Swaps)**:
  Vehicles operated by multiple drivers (e.g. V23, V19, V02) allow separating vehicle-intrinsic mechanical issues from driver behavior. Consistently high vibration across different drivers confirms a mechanical fault (suspension/engine/wheel alignment).

---

## 4. Key Assumptions & Limitations

1. **Sampling Frequency**: Telemetry is logged at 1-minute intervals. Sub-minute rapid spikes are proxied by per-minute deltas.
2. **Observation Window**: Data represents 1 week (ending 2026-08-06). Vehicle age and days since service are evaluated as of this date.
3. **Road Quality**: High IMU impact events may stem from poor road infrastructure; multi-driver aggregation mitigates driver bias.
