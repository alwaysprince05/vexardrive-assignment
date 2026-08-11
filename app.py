"""VexarDrive Fleet Analytics — Executive-Grade Streamlit Multi-Page Dashboard.

Run:  .venv/bin/streamlit run app.py
Pages: Executive Overview | Driver Behaviour & Safety | Vehicle Health | Methodology
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="VexarDrive Fleet Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Processed Data
DATA = "data"

@st.cache_data
def load():
    d = pd.read_parquet(f"{DATA}/driver_scores.parquet")
    v = pd.read_parquet(f"{DATA}/vehicle_scores.parquet")
    t = pd.read_parquet(f"{DATA}/trips.parquet")
    tl = pd.read_parquet(f"{DATA}/telemetry.parquet")
    return d, v, t, tl

d, v, t, tl = load()

# Curated Palette & Design System
RISK_COLORS = {
    "Low": "#00E676",       # Neon Emerald
    "Moderate": "#FFD600",  # Vivid Amber
    "High": "#FF9100",      # Deep Orange
    "Critical": "#FF5252"   # Glowing Crimson
}

HEALTH_COLORS = {
    "Healthy": "#00E676",   # Neon Emerald
    "Monitor": "#FFD600",   # Vivid Amber
    "Watch": "#FF9100",     # Deep Orange
    "High Risk": "#FF5252"  # Glowing Crimson
}

DRIVER_WEIGHTS_MAP = {
    "speeding_rate_pct": 0.40,
    "harsh_brake_rate_pct": 0.25,
    "harsh_accel_rate_pct": 0.20,
    "impact_rate_pct": 0.10,
    "aggressive_turn_rate_pct": 0.05
}

# Initialize Navigation Session State
if "page" not in st.session_state:
    st.session_state.page = "Executive Overview"

# Comprehensive Ultra-Modern CSS Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Remove Top Header White Bar & Decoration Strip */
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    header[data-testid="stHeader"] {
        background-color: #0B0E14 !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    header[data-testid="stHeader"] * {
        color: #94A3B8 !important;
    }
    
    /* Main Background */
    .stApp {
        background-color: #0B0E14 !important;
        color: #E2E8F0 !important;
    }
    
    .block-container {
        padding-top: 1.6rem !important;
        padding-bottom: 3rem !important;
        max-width: 1400px !important;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0F141C !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        display: flex !important;
        flex-direction: column !important;
        height: 100% !important;
    }
    
    /* Transform Sidebar Buttons into Premium Navigation Tab Cards */
    div[data-testid="stSidebar"] button {
        width: 100% !important;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        color: #94A3B8 !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        text-align: left !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin-bottom: 8px !important;
        display: flex !important;
        justify-content: flex-start !important;
        align-items: center !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
    }
    
    div[data-testid="stSidebar"] button:hover {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.15) 0%, rgba(30, 41, 59, 0.8) 100%) !important;
        border-color: rgba(56, 189, 248, 0.4) !important;
        color: #38BDF8 !important;
        transform: translateX(4px) !important;
        box-shadow: 0 4px 16px rgba(56, 189, 248, 0.15) !important;
    }
    
    /* Active Button Style */
    div[data-testid="stSidebar"] button.nav-active {
        background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%) !important;
        border-color: #38BDF8 !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 20px rgba(14, 165, 233, 0.4) !important;
    }
    
    /* Card Container */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.4);
    }
    .metric-title {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94A3B8;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.95rem;
        font-weight: 800;
        color: #F8FAFC;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .metric-subtitle {
        font-size: 0.78rem;
        color: #38BDF8;
        margin-top: 4px;
        font-weight: 600;
    }
    
    /* Proposal Box Styling */
    .proposal-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 16px;
    }
    .proposal-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #38BDF8;
        margin-bottom: 6px;
    }
    .proposal-body {
        font-size: 0.88rem;
        color: #CBD5E1;
        line-height: 1.6;
    }

    /* Category Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    .badge-critical, .badge-high-risk { background: rgba(255, 82, 82, 0.15); color: #FF5252; border: 1px solid #FF5252; }
    .badge-high, .badge-watch { background: rgba(255, 145, 0, 0.15); color: #FF9100; border: 1px solid #FF9100; }
    .badge-moderate, .badge-monitor { background: rgba(255, 214, 0, 0.15); color: #FFD600; border: 1px solid #FFD600; }
    .badge-low, .badge-healthy { background: rgba(0, 230, 118, 0.15); color: #00E676; border: 1px solid #00E676; }
    
    /* Header Banner */
    .header-banner {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border-left: 5px solid #38BDF8;
        border-radius: 14px;
        padding: 22px 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    }
    .header-title {
        font-size: 1.75rem;
        font-weight: 800;
        color: #F8FAFC;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .header-desc {
        font-size: 0.92rem;
        color: #94A3B8;
        margin-top: 6px;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #0F141C;
        padding: 8px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 600;
        padding: 10px 18px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E293B !important;
        color: #38BDF8 !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to apply Plotly dark template styling
def style_plotly_fig(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.5)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#CBD5E1"),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)")
    )
    return fig

# Helper function to render assignment footer card at bottom of sidebar
def render_sidebar_footer():
    st.sidebar.markdown("<div style='margin-top: 36px;'></div>", unsafe_allow_html=True)
    st.sidebar.markdown("""
    <div style='background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 16px; font-size: 0.78rem; color: #94A3B8;'>
        <div style='font-weight: 800; color: #F8FAFC; margin-bottom: 4px; font-size: 0.88rem; letter-spacing: -0.01em;'>VexarDrive × Polaris</div>
        <div style='color: #64748B; font-size: 0.76rem; font-weight: 500;'>Candidate Evaluation Solution</div>
        <div style='margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.06); color: #38BDF8; font-weight: 600; line-height: 1.6;'>
            • 30 Drivers | 30 Vehicles<br>
            • 450 Trips | 12,987 Logs
        </div>
    </div>
    """, unsafe_allow_html=True)

# Sidebar Header Logo Banner (Clean Text Branding)
st.sidebar.markdown("""
<div style='background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%); 
            border: 1px solid rgba(56, 189, 248, 0.25); 
            border-radius: 14px; 
            padding: 18px 14px; 
            text-align: center; 
            margin-bottom: 22px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);'>
    <div style='display: flex; align-items: center; justify-content: center; gap: 8px;'>
        <span style='font-size: 1.55rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.02em;'>Vexar<span style='color: #38BDF8;'>Drive</span></span>
    </div>
    <div style='margin-top: 6px;'>
        <span style='background: rgba(56, 189, 248, 0.15); color: #38BDF8; font-size: 0.68rem; font-weight: 800; padding: 3px 10px; border-radius: 12px; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(56, 189, 248, 0.3);'>
            Fleet Telemetry Analytics
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style='font-size: 0.72rem; font-weight: 700; color: #64748B; letter-spacing: 0.08em; text-transform: uppercase; margin-left: 4px; margin-bottom: 10px;'>
    NAVIGATION MENU
</div>
""", unsafe_allow_html=True)

# Clean Button Navigation (Zero Emojis!)
nav_items = [
    ("Executive Overview", "Executive Overview"),
    ("Driver Behaviour & Safety", "Driver Behaviour & Safety"),
    ("Vehicle Health & Maintenance", "Vehicle Health & Maintenance"),
    ("Methodology & Data Quality", "Methodology & Data Quality")
]

for label, val in nav_items:
    is_active = (st.session_state.page == val)
    btn_type = "primary" if is_active else "secondary"
    if st.sidebar.button(label, key=f"nav_btn_{val}", use_container_width=True, type=btn_type):
        st.session_state.page = val
        st.rerun()

page = st.session_state.page


# ==============================================================================
# 1. EXECUTIVE OVERVIEW
# ==============================================================================
if page == "Executive Overview":
    render_sidebar_footer()
    
    st.markdown("""
    <div class="header-banner">
        <h1 class="header-title">Executive Fleet Risk & Health Overview</h1>
        <p class="header-desc">Unified telematics diagnostic monitoring for delivery two-wheeler operations</p>
    </div>
    """, unsafe_allow_html=True)

    # 5 KPI Metric Cards
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Active Drivers</div>
            <div class="metric-value">{len(d)}</div>
            <div class="metric-subtitle">30 primary assignments</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Active Vehicles</div>
            <div class="metric-value">{len(v)}</div>
            <div class="metric-subtitle">Two-wheeler fleet</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Trips</div>
            <div class="metric-value">{len(t)}</div>
            <div class="metric-subtitle">15 trips per driver</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Distance (Corrected)</div>
            <div class="metric-value">{t['Distance_KM_Corrected'].sum():,.0f} <span style='font-size: 1rem;'>km</span></div>
            <div class="metric-subtitle">Kinematic ground truth</div>
        </div>
        """, unsafe_allow_html=True)

    with k5:
        crit_count = int((d.risk_category == "Critical").sum())
        st.markdown(f"""
        <div class="metric-card" style="border-color: rgba(255, 82, 82, 0.4);">
            <div class="metric-title" style="color: #FF5252;">Critical Risk Drivers</div>
            <div class="metric-value" style="color: #FF5252;">{crit_count}</div>
            <div class="metric-subtitle" style="color: #FF8A8A;">Requires safety action</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Fleet Risk & Health Breakdown Charts
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Driver Risk Category Breakdown")
        df_risk = d.risk_category.value_counts().reindex(["Low", "Moderate", "High", "Critical"]).reset_index()
        df_risk.columns = ["Category", "Count"]
        fig = px.bar(
            df_risk, x="Category", y="Count", color="Category",
            color_discrete_map=RISK_COLORS,
            text="Count"
        )
        fig.update_traces(textposition="outside", marker=dict(cornerradius=6))
        fig.update_layout(showlegend=False, height=350, yaxis_title="Number of Drivers")
        st.plotly_chart(style_plotly_fig(fig), width="stretch")

    with c2:
        st.subheader("Vehicle Maintenance Health Breakdown")
        df_health = v.health_category.value_counts().reindex(["Healthy", "Monitor", "Watch", "High Risk"]).reset_index()
        df_health.columns = ["Category", "Count"]
        fig = px.bar(
            df_health, x="Category", y="Count", color="Category",
            color_discrete_map=HEALTH_COLORS,
            text="Count"
        )
        fig.update_traces(textposition="outside", marker=dict(cornerradius=6))
        fig.update_layout(showlegend=False, height=350, yaxis_title="Number of Vehicles")
        st.plotly_chart(style_plotly_fig(fig), width="stretch")

    st.markdown("<br>", unsafe_allow_html=True)

    # 2D Scatter: Driver Risk vs Exposure
    st.subheader("Driver Safety Risk vs. Distance Driven (Exposure)")
    fig = px.scatter(
        d, x="exposure_km", y="risk_score", size="trips", color="risk_category",
        color_discrete_map=RISK_COLORS,
        hover_name="Driver_Name",
        hover_data={"Driver_ID": True, "max_speed": ":.1f km/h", "speeding_rate_per100km": ":.1f", "exposure_km": ":.1f km"},
        labels={"exposure_km": "Distance Driven (km)", "risk_score": "Driver Risk Score (0-100)"}
    )
    fig.update_traces(marker=dict(line=dict(width=1, color="rgba(255,255,255,0.4)")))
    fig.update_layout(height=450)
    st.plotly_chart(style_plotly_fig(fig), width="stretch")


# ==============================================================================
# 2. DRIVER BEHAVIOUR & SAFETY
# ==============================================================================
elif page == "Driver Behaviour & Safety":
    # Sidebar Filters
    st.sidebar.markdown("""
    <div style='font-size: 0.72rem; font-weight: 700; color: #64748B; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 14px; margin-bottom: 6px;'>
        DRIVER FILTERS
    </div>
    """, unsafe_allow_html=True)
    hubs = st.sidebar.multiselect("Home Hub Filter", sorted(d.Home_Hub.unique()), default=sorted(d.Home_Hub.unique()))
    cats = st.sidebar.multiselect("Risk Category Filter", ["Low", "Moderate", "High", "Critical"], default=["Low", "Moderate", "High", "Critical"])
    
    render_sidebar_footer()

    dd = d[d.Home_Hub.isin(hubs) & d.risk_category.isin(cats)]

    st.markdown("""
    <div class="header-banner">
        <h1 class="header-title">Driver Behaviour & Safety Risk Engine</h1>
        <p class="header-desc">Identify, rank, and diagnose high-risk driving behaviors normalized per 100 km</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick Summary Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Selected Drivers", len(dd))
    m2.metric("Fleet Avg Risk Score", f"{dd.risk_score.mean():.1f} / 100")
    m3.metric("Avg Speeding Rate", f"{dd.speeding_rate_per100km.mean():.1f} / 100 km")
    m4.metric("Avg Harsh Brakes", f"{dd.harsh_brake_rate_per100km.mean():.1f} / 100 km")

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Driver Risk Ranking", "Driver Inspector", "Speed Distribution"])

    with tab1:
        st.subheader("Driver Safety Risk Ranking (0 = Safest, 100 = Riskiest)")
        fig = px.bar(
            dd.sort_values("risk_score"), x="risk_score", y="Driver_Name", orientation="h",
            color="risk_category", color_discrete_map=RISK_COLORS,
            hover_data={"Driver_ID": True, "exposure_km": ":.1f", "max_speed": ":.1f"},
            labels={"risk_score": "Risk Score (0-100)", "Driver_Name": ""}
        )
        fig.update_layout(height=720, yaxis=dict(autorange="reversed"))
        st.plotly_chart(style_plotly_fig(fig), width="stretch")

        st.subheader("Top Riskiest Drivers Component Breakdown (Percentile Ranks)")
        top10 = dd.nlargest(10, "risk_score")
        comp_cols = ["speeding_rate_pct", "harsh_brake_rate_pct", "harsh_accel_rate_pct", "impact_rate_pct", "aggressive_turn_rate_pct"]
        labels = ["Speeding (40%)", "Harsh Brake (25%)", "Harsh Accel (20%)", "Impact (10%)", "Aggressive Turn (5%)"]
        
        fig = go.Figure()
        for c, label in zip(comp_cols, labels):
            fig.add_trace(go.Bar(name=label, y=top10.Driver_Name, x=top10[c] * DRIVER_WEIGHTS_MAP[c], orientation="h"))
        fig.update_layout(barmode="stack", height=450, xaxis_title="Weighted Contribution to Risk Score", yaxis=dict(autorange="reversed"))
        st.plotly_chart(style_plotly_fig(fig), width="stretch")

    with tab2:
        st.subheader("Individual Driver Telematics Profile")
        selected_driver = st.selectbox("Select Driver to Inspect", dd.sort_values("risk_score", ascending=False)["Driver_Name"])
        d_row = dd[dd.Driver_Name == selected_driver].iloc[0]

        # Driver Profile Card
        r_cat = d_row["risk_category"]
        badge_cls = f"badge-{r_cat.lower()}"
        
        c_left, c_right = st.columns([1, 2])
        with c_left:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid {RISK_COLORS.get(r_cat, '#38BDF8')};">
                <h3 style="margin: 0; color: #F8FAFC;">{d_row['Driver_Name']}</h3>
                <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 2px;">ID: <strong>{d_row['Driver_ID']}</strong> | Hub: <strong>{d_row['Home_Hub']}</strong></p>
                <div style="margin-top: 12px;">
                    <span class="badge {badge_cls}">{r_cat} Risk</span>
                    <h2 style="margin: 8px 0 0 0; color: {RISK_COLORS.get(r_cat, '#F8FAFC')}; font-size: 2.4rem;">{d_row['risk_score']:.1f} <span style="font-size: 1rem; color: #94A3B8;">/ 100</span></h2>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.write(f"**Age**: {d_row['Age']} years | **Gender**: {d_row['Gender']}")
            st.write(f"**Experience**: {d_row['License_Experience_Years']} years")
            st.write(f"**Assigned Vehicle**: {d_row['Primary_Vehicle_ID']}")
            st.write(f"**Total Distance**: {d_row['exposure_km']:.1f} km across {d_row['trips']} trips")

        with c_right:
            st.markdown("#### Violation Metrics per 100 km")
            p1, p2, p3 = st.columns(3)
            p1.metric("Speeding Events", f"{d_row['speeding_rate_per100km']:.1f} / 100 km")
            p2.metric("Harsh Brakes", f"{d_row['harsh_brake_rate_per100km']:.1f} / 100 km")
            p3.metric("Harsh Accels", f"{d_row['harsh_accel_rate_per100km']:.1f} / 100 km")

            p4, p5, p6 = st.columns(3)
            p4.metric("Impact / Bumps", f"{d_row['impact_rate_per100km']:.1f} / 100 km")
            p5.metric("Aggressive Turns", f"{d_row['aggressive_turn_rate_per100km']:.1f} / 100 km")
            p6.metric("Max Speed Recorded", f"{d_row['max_speed']:.1f} km/h")

    with tab3:
        st.subheader("Fleet Instantaneous Speed Distribution (12,987 Telemetry Logs)")
        fig = px.histogram(tl, x="Speed_kmph", nbins=60, labels={"Speed_kmph": "Speed (km/h)"}, color_discrete_sequence=["#38BDF8"])
        fig.add_vline(x=50, line_dash="dash", line_color="#FF5252", annotation_text="Speeding Threshold 50 km/h (P99)", annotation_font_color="#FF5252")
        st.plotly_chart(style_plotly_fig(fig), width="stretch")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Complete Driver Master Dataset")
    st.dataframe(
        dd[["Driver_ID", "Driver_Name", "Home_Hub", "trips", "exposure_km", "max_speed",
            "speeding_rate_per100km", "harsh_brake_rate_per100km", "harsh_accel_rate_per100km",
            "impact_rate_per100km", "risk_score", "risk_category"]]
        .sort_values("risk_score", ascending=False)
        .style.background_gradient(subset=["risk_score"], cmap="RdYlGn_r"),
        width="stretch",
        height=400
    )


# ==============================================================================
# 3. VEHICLE HEALTH & MAINTENANCE
# ==============================================================================
elif page == "Vehicle Health & Maintenance":
    # Sidebar Filters
    st.sidebar.markdown("""
    <div style='font-size: 0.72rem; font-weight: 700; color: #64748B; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 14px; margin-bottom: 6px;'>
        VEHICLE FILTERS
    </div>
    """, unsafe_allow_html=True)
    vcats = st.sidebar.multiselect("Health Category Filter", ["Healthy", "Monitor", "Watch", "High Risk"], default=["Healthy", "Monitor", "Watch", "High Risk"])
    
    render_sidebar_footer()

    vv = v[v.health_category.isin(vcats)]

    st.markdown("""
    <div class="header-banner">
        <h1 class="header-title">Vehicle Health & Maintenance Diagnostics</h1>
        <p class="header-desc">Identify mechanical degradation, engine idle roughness, and chassis vibration anomalies</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick Summary Metrics
    v1, v2, v3, v4 = st.columns(4)
    v1.metric("Selected Vehicles", len(vv))
    v2.metric("Avg Maintenance Risk", f"{vv.maintenance_risk.mean():.1f} / 100")
    v3.metric("Vehicles in Watch/High Risk", int(v.health_category.isin(["Watch", "High Risk"]).sum()))
    v4.metric("Shared Multi-Driver Vehicles", int((v.n_drivers > 1).sum()))

    st.markdown("<br>", unsafe_allow_html=True)

    tab_v1, tab_v2, tab_v3 = st.tabs(["Maintenance Risk Ranking", "Cross-Driver Vehicle Swap Validation", "Vehicle Inspector"])

    with tab_v1:
        st.subheader("Vehicle Maintenance Risk Ranking (0 = Healthy, 100 = High Risk)")
        fig = px.bar(
            vv.sort_values("maintenance_risk"), x="maintenance_risk", y="Vehicle_ID", orientation="h",
            color="health_category", color_discrete_map=HEALTH_COLORS,
            hover_data={"Make": True, "Model": True, "Vehicle_Age_Years": ":.1f yrs", "Days_Since_Service": True, "n_drivers": True},
            labels={"maintenance_risk": "Maintenance Risk Score (0-100)", "Vehicle_ID": ""}
        )
        fig.update_layout(height=720, yaxis=dict(autorange="reversed"))
        st.plotly_chart(style_plotly_fig(fig), width="stretch")

        st.subheader("Chassis Vibration (20-40 km/h Band) vs. Vehicle Age")
        fig = px.scatter(
            vv, x="Vehicle_Age_Years", y="vib_band_mean", size="Days_Since_Service",
            color="health_category", color_discrete_map=HEALTH_COLORS,
            hover_name="Vehicle_ID", hover_data={"Make": True, "Model": True, "n_drivers": True, "maintenance_risk": ":.1f"},
            labels={"Vehicle_Age_Years": "Vehicle Age (Years)", "vib_band_mean": "Normalized Chassis Vibration (|a-1g|)"}
        )
        st.plotly_chart(style_plotly_fig(fig), width="stretch")

    with tab_v2:
        st.subheader("Cross-Driver Vehicle Swap Analysis")
        st.info("Methodological Insight: Vehicles operated by multiple drivers allow separating intrinsic vehicle mechanical faults from individual driver style. When high vibration persists across multiple different drivers (e.g. V23, V19), it confirms a physical mechanical issue (e.g., degraded suspension/engine mounts).")
        
        sw = vv[vv.n_drivers > 1][["Vehicle_ID", "Make", "Model", "n_drivers", "vib_band_mean",
                                   "idle_roughness", "Days_Since_Service", "maintenance_risk",
                                   "health_category"]].sort_values("maintenance_risk", ascending=False)
        st.dataframe(
            sw.round(3).style.background_gradient(subset=["maintenance_risk"], cmap="RdYlGn_r"),
            width="stretch"
        )

    with tab_v3:
        st.subheader("Individual Vehicle Technical Profile")
        selected_veh = st.selectbox("Select Vehicle to Inspect", vv.sort_values("maintenance_risk", ascending=False)["Vehicle_ID"])
        v_row = vv[vv.Vehicle_ID == selected_veh].iloc[0]

        h_cat = v_row["health_category"]
        badge_cls = f"badge-{h_cat.lower().replace(' ', '-')}"

        vc_left, vc_right = st.columns([1, 2])
        with vc_left:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid {HEALTH_COLORS.get(h_cat, '#38BDF8')};">
                <h3 style="margin: 0; color: #F8FAFC;">{v_row['Vehicle_ID']} — {v_row['Make']} {v_row['Model']}</h3>
                <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 2px;">Type: <strong>{v_row['Vehicle_Type']}</strong></p>
                <div style="margin-top: 12px;">
                    <span class="badge {badge_cls}">{h_cat}</span>
                    <h2 style="margin: 8px 0 0 0; color: {HEALTH_COLORS.get(h_cat, '#F8FAFC')}; font-size: 2.4rem;">{v_row['maintenance_risk']:.1f} <span style="font-size: 1rem; color: #94A3B8;">/ 100</span></h2>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.write(f"**Vehicle Age**: {v_row['Vehicle_Age_Years']} years")
            st.write(f"**Days Since Last Service**: {v_row['Days_Since_Service']} days")
            st.write(f"**Number of Drivers**: {v_row['n_drivers']} drivers")
            st.write(f"**Est. Odometer**: {v_row['est_odometer_km']:,.0f} km")

        with vc_right:
            st.markdown("#### Diagnostic Telematics Metrics")
            vp1, vp2 = st.columns(2)
            vp1.metric("Vibration Band Mean (20-40km/h)", f"{v_row['vib_band_mean']:.4f} g")
            vp2.metric("Idle Engine Roughness", f"{v_row['idle_roughness']:.4f} g")

            vp3, vp4 = st.columns(2)
            vp3.metric("Impact Event Rate", f"{v_row['impact_rate']:.1f} / 100 km")
            vp4.metric("Rotation Event Rate", f"{v_row['rotation_rate']:.1f} / 100 km")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Complete Vehicle Master Dataset")
    st.dataframe(
        vv[["Vehicle_ID", "Make", "Model", "Vehicle_Type", "Vehicle_Age_Years",
            "Days_Since_Service", "est_odometer_km", "n_drivers", "exposure_km",
            "vib_band_mean", "idle_roughness", "maintenance_risk", "health_category"]]
        .sort_values("maintenance_risk", ascending=False)
        .style.background_gradient(subset=["maintenance_risk"], cmap="RdYlGn_r"),
        width="stretch",
        height=400
    )


# ==============================================================================
# 4. METHODOLOGY & DATA QUALITY
# ==============================================================================
else:
    render_sidebar_footer()

    st.markdown("""
    <div class="header-banner">
        <h1 class="header-title">Methodology, Data Audit & Future Proposals</h1>
        <p class="header-desc">Technical specification, data verification checks, mathematical formulas, and strategic proposals beyond the dashboards</p>
    </div>
    """, unsafe_allow_html=True)

    tab_m1, tab_m2, tab_m3 = st.tabs(["Methodology & Data Audit", "Strategic Proposals (Beyond Dashboards)", "Full Candidate Documentation"])

    with tab_m1:
        st.markdown(r"""
        ### 1. Data Quality Findings & Kinematic Reconciliation
        
        | Check | Result | Action Taken |
        |---|---|---|
        | **Row Counts** | 30 drivers / 30 vehicles / 450 trips / 12,987 telemetry logs | 100% matched assignment brief |
        | **Nulls & Duplicates** | Zero missing values or duplicate timestamps | Trusted raw dataset integrity |
        | **Referential Integrity** | 100% join key match across Drivers, Vehicles, Trips & Telemetry | Trusted join structure |
        | **Telemetry Cadence** | Exactly 1 reading/min; rows = Duration_Min for all 450 trips | Verified timestamp regularity |
        | **Distance_KM Corruption** | **166 / 450 trips inconsistent** (median error 3.16 km) | **Re-derived exposure distance = Avg_Speed × Duration / 60** (matches telemetry to 0.01 km) |
        | **Speed Verification** | Avg/Max speed in Trips vs. Telemetry correlated at 1.00 | Trusted speed logs |

        ---

        ### 2. Event Thresholds & Statistical Basis

        | Event | Threshold | Statistical Justification |
        |---|---|---|
        | **Speeding** | $> 50\text{ km/h}$ | 99th percentile of speed distribution ($P_{99} = 51.3\text{ km/h}$) |
        | **Harsh Acceleration** | $> +20\text{ km/h per min}$ | Derived between $P_{90}$ ($18.5$) and $P_{95}$ ($25.4$) speed deltas |
        | **Harsh Braking** | $< -20\text{ km/h per min}$ | Derived between $P_{90}$ and $P_{95}$ speed deltas |
        | **Impact / Severe Bump** | $\text{accel\_mag} > 1.3g$ | $P_{99}$ accelerometer magnitude ($P_{99} = 1.43g$) |
        | **Aggressive Turn** | $\text{gyro\_mag} > 20\text{ dps}$ AND $\text{Speed} > 25\text{ km/h}$ | $P_{95}$ gyroscope reading with speed gating (filters 252 stationary handlebar turn artifacts) |

        ---

        ### 3. Mathematical Scoring Architecture

        - **Exposure Normalization**: Events are normalized **per 100 km** to eliminate exposure bias for high-mileage drivers.
        - **Percentile-Rank Transformation**: Robust against extreme outliers compared to standard min-max scaling.
        - **Driver Risk Formula**:
          $$\text{Driver Risk} = 0.40 \cdot \text{Speeding}_{\text{pct}} + 0.25 \cdot \text{Harsh Brake}_{\text{pct}} + 0.20 \cdot \text{Harsh Accel}_{\text{pct}} + 0.10 \cdot \text{Impact}_{\text{pct}} + 0.05 \cdot \text{Turn}_{\text{pct}}$$
        - **Vehicle Maintenance Risk Formula**:
          $$\text{Vehicle Risk} = 0.30 \cdot \text{Vibration}_{\text{score}} + 0.25 \cdot \text{Rotation}_{\text{score}} + 0.20 \cdot \text{Service Recency}_{\text{score}} + 0.15 \cdot \text{Age}_{\text{score}} + 0.10 \cdot \text{Usage}_{\text{score}}$$

        ---

        ### 4. Operational Assumptions & Limitations
        - **Phone Mount Orientation**: Orientation-invariant 3D vector magnitudes used due to unknown phone mounting angles.
        - **1-Minute Sampling Cadence**: Per-minute sampling acts as a proxy; rapid sub-second spikes are proxied by minute-level kinematics.
        - **Observation End Date**: Vehicle age and service recency computed as of **2026-08-06** (observation window end).
        """)

    with tab_m2:
        st.subheader("What Else Can This Telemetry Dataset Be Used For?")
        st.write("Beyond driver risk scoring and vehicle maintenance tracking, VexarDrive can leverage this smartphone sensor dataset for several high-impact business applications:")

        st.markdown("""
        <div class="proposal-card">
            <div class="proposal-title">1. Dynamic Usage-Based Insurance (UBI) & Automated Crash Reconstruction</div>
            <div class="proposal-body">
                • <strong>Pay-How-You-Drive Insurance</strong>: Transition fleet insurance from flat annual rates to dynamic risk-based pricing. Low-risk drivers (Score < 30) earn insurance premium rebates, reducing fleet overhead.<br>
                • <strong>Instant Crash Detection</strong>: When accelerometer magnitude spikes above 2.5g accompanied by an immediate speed drop to 0, trigger automated SOS dispatch and capture pre-impact telemetry for automated insurance claim processing.
            </div>
        </div>

        <div class="proposal-card">
            <div class="proposal-title">2. Crowdsourced Pothole & Road Quality Infrastructure Mapping</div>
            <div class="proposal-body">
                • <strong>Municipal Road Condition Index</strong>: By cross-referencing recurring high-g impact events (accel_mag > 1.3g) across multiple drivers at exact GPS coordinates, VexarDrive can generate a real-time road degradation heatmap.<br>
                • <strong>Smart Route Optimization</strong>: Dynamically reroute delivery riders around severely damaged roads to reduce cargo damage and extend vehicle suspension life.
            </div>
        </div>

        <div class="proposal-card">
            <div class="proposal-title">3. Driver Fatigue & Shift Safety Analytics</div>
            <div class="proposal-body">
                • <strong>Fatigue Curve Tracking</strong>: Measure risk score drift from Trip 1 to Trip 15 within a single shift. Spikes in harsh braking or speeding late in shifts highlight driver fatigue.<br>
                • <strong>Adaptive Workload Capping</strong>: Automatically recommend rest breaks or cap daily delivery orders when a driver's fatigue indicators exceed safe thresholds.
            </div>
        </div>

        <div class="proposal-card">
            <div class="proposal-title">4. Eco-Driving & Carbon Emissions Optimization</div>
            <div class="proposal-body">
                • <strong>Fuel Wastage Analytics</strong>: Quantify fuel wasted during excessive idle time (Speed < 3 km/h with engine running) and aggressive throttle bursts.<br>
                • <strong>Green Fleet Coaching</strong>: Provide drivers with eco-scorecards to minimize fuel consumption and lower operational CO2 emissions.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab_m3:
        st.subheader("Read Full Written Reports & Methodology Docs")
        st.write("You can read or download the complete candidate submission documents directly below:")

        with st.expander("Open EXECUTIVE_REPORT.md (Full Submission Report)", expanded=True):
            try:
                with open("EXECUTIVE_REPORT.md", "r") as f:
                    st.markdown(f.read())
            except Exception as e:
                st.error(f"Error loading EXECUTIVE_REPORT.md: {e}")

        with st.expander("Open METHODOLOGY.md (Formulas & Data Audit)", expanded=False):
            try:
                with open("METHODOLOGY.md", "r") as f:
                    st.markdown(f.read())
            except Exception as e:
                st.error(f"Error loading METHODOLOGY.md: {e}")
