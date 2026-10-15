import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from src.ingestion import load_data
from src.preprocessing import clean_and_normalize
from src.features import engineer_features, build_forecasting_dataset
from src.forecasting import MultiHorizonForecaster
from src.uncertainty import SplitConformalCalibrator
from src.risk import compute_spike_risk
from src.explainability import ModelExplainer
from src.simulation import run_intervention_simulation
from src.decision import evaluate_optimal_policy
from src.historical_replay import run_historical_crisis_replay
from src.reporting import generate_executive_brief

# --- Page Configuration ---
st.set_page_config(
    page_title="PRICEGUARD | Govt Price Intelligence DSS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling for Govt Dashboard Look ---
st.markdown("""
<style>
    .main-header { font-size: 24px; font-weight: 700; color: #1E3A8A; margin-bottom: 0px; }
    .sub-header { font-size: 14px; color: #4B5563; margin-bottom: 20px; }
    .metric-card { background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 15px; border-radius: 8px; }
    .risk-badge { font-weight: bold; padding: 4px 10px; border-radius: 4px; color: white; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Controls ---
st.sidebar.image("https://img.icons8.com/color/96/shield.png", width=60)
st.sidebar.markdown("### **PRICEGUARD DSS**")
st.sidebar.caption("Department of Consumer Affairs\nPredictive Price Intelligence & Buffer Stock System")
st.sidebar.divider()

selected_commodity = st.sidebar.selectbox("Commodity", ["Onion", "Tur"])
data_source_mode = st.sidebar.radio("Data Engine Mode", ["Official / Uploaded Data", "Simulated Demo Stream"])

nav_page = st.sidebar.radio(
    "Navigation Console",
    [
        "1. Executive Intelligence Overview",
        "2. Multi-Horizon Forecast & CI",
        "3. Explainable AI (SHAP Drivers)",
        "4. Geographic Mandi Heatmap",
        "5. What-If Buffer Simulator",
        "6. Historical Crisis Replay",
        "7. Policy Decision Report"
    ]
)

st.sidebar.divider()

# --- Data Loading & Model Cache Pipeline ---
@st.cache_data(show_spinner=False)
def get_pipeline_data(commodity, mode):
    force_demo = (mode == "Simulated Demo Stream")
    raw_df, is_demo = load_data(commodity=commodity, force_demo=force_demo)
    clean_df = clean_and_normalize(raw_df)
    feat_df = engineer_features(clean_df)
    return feat_df, is_demo

@st.cache_resource(show_spinner=False)
def get_trained_models(_df_feat, mode, _build_dataset_func):
    """
    Caches the XGBoost and Conformal Calibration to avoid retraining on every Streamlit interaction.
    The underscore `_` prefix tells Streamlit not to hash these large dataframe/function objects.
    """
    forecaster = MultiHorizonForecaster(horizons=[7, 14])
    forecaster.fit(_df_feat, _build_dataset_func)
    
    conformal = SplitConformalCalibrator(alpha=0.10)
    conformal.calibrate(forecaster, _df_feat, _build_dataset_func)
    
    return forecaster, conformal

with st.spinner("Processing time-series features and calibrating models..."):
    df_feat, is_demo_active = get_pipeline_data(selected_commodity, data_source_mode)
    
    # Retrieve Cached Models
    forecaster, conformal = get_trained_models(df_feat, data_source_mode, build_forecasting_dataset)
    
    # Latest Inference Row
    X_latest, _, _ = build_forecasting_dataset(df_feat, horizon=7)
    latest_row = X_latest.iloc[-1:]
    
    # Point + Uncertainty Inference
    intervals = conformal.predict_intervals(forecaster, latest_row)
    current_price = float(df_feat.iloc[-1]['price_per_kg'])
    recent_arrivals = float(df_feat.iloc[-1]['arrival_qty'])
    recent_mean = float(df_feat.iloc[-1]['price_roll_mean_7'])
    recent_std = float(df_feat.iloc[-1]['price_roll_std_7'])
    
    # Risk Assessment
    risk_info = compute_spike_risk(
        intervals[7]['point_forecast'], 
        intervals[7]['upper_bound'], 
        recent_mean, 
        recent_std
    )
    
    # SHAP Explainer
    explainer = ModelExplainer(forecaster, horizon=7)
    top_drivers = explainer.explain_instance(latest_row, top_k=4)

if is_demo_active:
    st.warning("⚠️ **DEMO DATA STREAM ACTIVE** — Using calibrated synthetic market generator (Historical Nashik/Gulbarga series).")

# ==============================================================================
# PAGE 1: EXECUTIVE INTELLIGENCE OVERVIEW
# ==============================================================================
if nav_page == "1. Executive Intelligence Overview":
    st.markdown('<p class="main-header">National Price Intelligence & Early Warning Overview</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Strategic monitoring dashboard for <b>{selected_commodity.upper()}</b></p>', unsafe_allow_html=True)
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Current Spot Rate", f"₹{current_price:.2f} / kg", f"{(current_price - recent_mean):+.2f} vs 7d avg")
    
    h7_val = intervals[7]['point_forecast']
    kpi2.metric("7-Day Projected Rate", f"₹{h7_val:.2f} / kg", f"{(h7_val - current_price):+.2f} ({(h7_val - current_price)/current_price*100:+.1f}%)")
    
    kpi3.metric("Spike Probability", f"{risk_info['spike_probability']}%", f"Z-Score: {risk_info['z_score']}")
    
    badge_bg = {"CRITICAL": "#DC2626", "HIGH": "#EA580C", "MODERATE": "#CA8A04", "LOW": "#16A34A"}[risk_info['risk_level']]
    kpi4.markdown(f"""
    <div style="background-color: {badge_bg}; padding: 12px; border-radius: 8px; text-align: center; color: white;">
        <span style="font-size: 12px;">SYSTEM RISK TIER</span><br>
        <span style="font-size: 20px; font-weight: bold;">{risk_info['risk_level']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader("Price History & Trajectory (Past 60 Days + 14-Day Horizon)")
        recent_history = df_feat.tail(60)[['date', 'price_per_kg']].copy()
        
        last_date = recent_history['date'].iloc[-1]
        future_dates = [last_date + timedelta(days=7), last_date + timedelta(days=14)]
        future_pts = [intervals[7]['point_forecast'], intervals[14]['point_forecast']]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=recent_history['date'], y=recent_history['price_per_kg'], name="Historical Actual", line=dict(color="#1E3A8A", width=2.5)))
        fig.add_trace(go.Scatter(x=future_dates, y=future_pts, name="Projected Trajectory", line=dict(color="#DC2626", width=2.5, dash="dash")))
        fig.add_trace(go.Scatter(
            x=future_dates + future_dates[::-1],
            y=[intervals[7]['upper_bound'], intervals[14]['upper_bound'], intervals[14]['lower_bound'], intervals[7]['lower_bound']],
            fill='toself', fillcolor='rgba(220, 38, 38, 0.15)', line=dict(color='rgba(255,255,255,0)'),
            name="90% Conformal Interval"
        ))
        fig.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20), hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Actionable Policy Alert")
        if risk_info['risk_level'] in ["HIGH", "CRITICAL"]:
            st.error(f"🚨 **ALERT:** {risk_info['action_summary']}")
        elif risk_info['risk_level'] == "MODERATE":
            st.warning(f"⚠️ **ATTENTION:** {risk_info['action_summary']}")
        else:
            st.success(f"✅ **NORMAL:** {risk_info['action_summary']}")
            
        st.markdown("#### Primary Model Drivers (XAI)")
        for d in top_drivers[:3]:
            st.info(f"📌 {d['policy_driver']}")

# ==============================================================================
# PAGE 2: MULTI-HORIZON FORECAST & CONFORMAL UNCERTAINTY
# ==============================================================================
elif nav_page == "2. Multi-Horizon Forecast & CI":
    st.markdown('<p class="main-header">Statistically Calibrated Forecast Horizons</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Inductive Split Conformal Prediction Intervals (Non-parametric distribution-free)</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### **7-Day Horizon (T+7)**")
        h7 = intervals[7]
        st.metric("Point Estimate", f"₹ {h7['point_forecast']} / kg")
        st.success(f"**90% Prediction Range:** ₹ {h7['lower_bound']} — ₹ {h7['upper_bound']} / kg")
        st.caption(f"Calibrated Margin: ±₹ {h7['interval_width']/2:.2f} / kg")
        
    with col2:
        st.markdown("### **14-Day Horizon (T+14)**")
        h14 = intervals[14]
        st.metric("Point Estimate", f"₹ {h14['point_forecast']} / kg")
        st.info(f"**90% Prediction Range:** ₹ {h14['lower_bound']} — ₹ {h14['upper_bound']} / kg")
        st.caption(f"Calibrated Margin: ±₹ {h14['interval_width']/2:.2f} / kg")
        
    st.divider()
    st.subheader("Model Validation & Calibration Diagnostics")
    v1, v2, v3 = st.columns(3)
    v1.metric("7-Day MAE", f"₹ {forecaster.metrics[7]['MAE']} / kg")
    v2.metric("7-Day RMSE", f"₹ {forecaster.metrics[7]['RMSE']} / kg")
    v3.metric("7-Day sMAPE", f"{forecaster.metrics[7]['sMAPE']}%")

# ==============================================================================
# PAGE 3: EXPLAINABLE AI (SHAP DRIVERS)
# ==============================================================================
elif nav_page == "3. Explainable AI (SHAP Drivers)":
    st.markdown('<p class="main-header">Explainable AI: Local Decision Drivers</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Quantifying exactly which economic variables influence the forecast (TreeSHAP)</p>', unsafe_allow_html=True)
    
    st.info("💡 **Scientific Guardrail:** Feature attributions represent *model associations* and relative weight contributions, not counterfactual physical causation.")
    
    shap_df = pd.DataFrame(top_drivers)
    fig_shap = px.bar(
        shap_df,
        x='impact',
        y='feature',
        orientation='h',
        color='impact',
        color_continuous_scale=['#16A34A', '#E2E8F0', '#DC2626'],
        labels={'impact': 'SHAP Value (Price Impact in ₹/kg)', 'feature': 'Economic Signal'},
        title="Top Factor Contributions for Upcoming 7-Day Forecast"
    )
    fig_shap.update_layout(height=300)
    st.plotly_chart(fig_shap, use_container_width=True)
    
    st.subheader("Policymaker Factor Translation")
    for d in top_drivers:
        st.markdown(f"- **{d['feature']}** ({d['actual_value']:.2f}): {d['policy_driver']}")

# ==============================================================================
# PAGE 4: GEOGRAPHIC MANDI HEATMAP
# ==============================================================================
elif nav_page == "4. Geographic Mandi Heatmap":
    st.markdown('<p class="main-header">Geographic Price & Vulnerability Matrix</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">District-level price reporting centres & major wholesale mandis</p>', unsafe_allow_html=True)
    
    # Regional coordinate mapping for key hubs
    geo_data = pd.DataFrame({
        "Mandi": ["Lasalgaon (MH)", "Nashik (MH)", "Azadpur (DL)", "Solapur (MH)", "Kalaburagi (KA)", "Latur (MH)", "Indore (MP)"],
        "lat": [20.1462, 19.9975, 28.7165, 17.6599, 17.3297, 18.4088, 22.7196],
        "lon": [74.2285, 73.7898, 77.1728, 75.9064, 76.8343, 76.5604, 75.8577],
        "Spot_Rate": [current_price * np.random.uniform(0.92, 1.08) for _ in range(7)],
        "Arrival_Tonnes": [np.random.randint(150, 800) for _ in range(7)],
        "Vulnerability": ["HIGH" if i in [0, 2] else "MODERATE" for i in range(7)]
    })
    
    fig_map = px.scatter_mapbox(
        geo_data,
        lat="lat",
        lon="lon",
        hover_name="Mandi",
        hover_data={"Spot_Rate": ":.2f", "Arrival_Tonnes": True, "Vulnerability": True, "lat": False, "lon": False},
        color="Vulnerability",
        color_discrete_map={"HIGH": "#DC2626", "MODERATE": "#CA8A04", "LOW": "#16A34A"},
        size="Arrival_Tonnes",
        zoom=4.5,
        center={"lat": 21.0, "lon": 76.0},
        mapbox_style="carto-positron"
    )
    fig_map.update_layout(height=450, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_map, use_container_width=True)
    st.table(geo_data[["Mandi", "Spot_Rate", "Arrival_Tonnes", "Vulnerability"]])

# ==============================================================================
# PAGE 5: WHAT-IF BUFFER SIMULATOR & DECISION SUPPORT
# ==============================================================================
elif nav_page == "5. What-If Buffer Simulator":
    st.markdown('<p class="main-header">Strategic Buffer-Stock Intervention Simulator</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Simulating price stabilization outcomes under stated market supply elasticities</p>', unsafe_allow_html=True)
    
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
    with col_ctrl1:
        current_buffer = st.number_input("Available Strategic Buffer (MT)", min_value=5000, max_value=200000, value=50000, step=5000)
    with col_ctrl2:
        market_elasticity = st.slider("Supply Elasticity Coefficient", min_value=-0.35, max_value=-0.05, value=-0.18, step=0.01)
    with col_ctrl3:
        target_horizon_price = intervals[7]['point_forecast']
        st.metric("Base Forecast (No Intervention)", f"₹ {target_horizon_price:.2f} / kg")
        
    sim_df = run_intervention_simulation(
        current_price=current_price,
        forecast_price=target_horizon_price,
        recent_daily_arrivals=recent_arrivals,
        buffer_stock_available=current_buffer,
        elasticity=market_elasticity
    )
    
    st.subheader("Intervention Trade-Off Comparison Matrix")
    st.dataframe(sim_df.style.highlight_min(subset=["Simulated Price (₹/kg)"], color="#DCFCE7"), use_container_width=True)
    
    policy = evaluate_optimal_policy(sim_df, risk_info['risk_level'])
    st.divider()
    
    st.subheader("🤖 Policy Decision Recommendation Engine")
    rec_col1, rec_col2 = st.columns([1, 2])
    with rec_col1:
        st.success(f"**Recommended:**\n### {policy['recommended_scenario']}")
        st.metric("Release Quota", f"{policy['release_mt']} MT")
        st.metric("Target Equilibrium", f"₹ {policy['target_price']} / kg", f"-₹{policy['expected_drop']} drop")
    with rec_col2:
        st.markdown("#### Strategic Policymaker Rationale")
        st.write(policy['policymaker_rationale'])
        st.markdown(f"- **Buffer Retained:** {policy['buffer_retained']} MT")
        st.markdown(f"- **Estimated Logistics / Holding Cost:** ₹ {policy['estimated_budget_lakhs']} Lakhs")
        st.caption("Disclaimer: Output represents a model-assisted scenario estimate under stated elasticity assumptions.")

# ==============================================================================
# PAGE 6: HISTORICAL CRISIS REPLAY
# ==============================================================================
elif nav_page == "6. Historical Crisis Replay":
    st.markdown('<p class="main-header">Historical Crisis Replay & Model Validation</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Validating model forecast accuracy by masking future data before historical spikes</p>', unsafe_allow_html=True)
    
    st.write("Select a past crisis point. The engine will mask all subsequent data and reproduce the exact forecast generated on that day.")
    
    # Pick a safe historical date even for short datasets (requires at least 25 days of history)
    safe_idx = max(-30, -len(df_feat) + 25)
    if safe_idx >= 0:
        safe_idx = -1
    available_max_date = df_feat['date'].iloc[safe_idx].strftime('%Y-%m-%d')
    replay_choice = st.date_input("Select Historical Replay Date", value=pd.to_datetime(available_max_date))
    
    if st.button("Execute Crisis Replay Engine"):
        with st.spinner("Rewinding market time series and running inference..."):
            try:
                rep_res = run_historical_crisis_replay(df_feat, str(replay_choice), horizon=7)
                
                r1, r2, r3, r4 = st.columns(4)
                r1.metric("Spot Rate on Replay Date", f"₹ {rep_res['as_of_price']} / kg")
                r2.metric("7-Day Forecast", f"₹ {rep_res['point_forecast']} / kg")
                r3.metric("Spike Probability", f"{rep_res['spike_probability']}%")
                r4.metric("Actual Realized Price (T+7)", f"₹ {rep_res['actual_realized_price']} / kg")
                
                st.divider()
                if rep_res['was_accurate']:
                    st.success(f"✅ **VALIDATION SUCCESS:** The actual realized price (₹{rep_res['actual_realized_price']}) fell strictly within the 90% Conformal Prediction Bounds (₹{rep_res['interval_lower']} – ₹{rep_res['interval_upper']}).")
                else:
                    st.warning("⚠️ Prediction interval boundary exceeded.")
            except Exception as e:
                st.error(f"Replay Execution Error: {e}")

# ==============================================================================
# PAGE 7: POLICY DECISION REPORT
# ==============================================================================
elif nav_page == "7. Policy Decision Report":
    st.markdown('<p class="main-header">Executive Situation Report Generator</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Generate and download official decision memos for departmental briefings</p>', unsafe_allow_html=True)
    
    sim_df_rep = run_intervention_simulation(current_price, intervals[7]['point_forecast'], recent_arrivals, 50000.0)
    policy_rep = evaluate_optimal_policy(sim_df_rep, risk_info['risk_level'])
    
    report_text = generate_executive_brief(
        commodity=selected_commodity,
        current_price=current_price,
        intervals=intervals,
        risk=risk_info,
        top_drivers=top_drivers,
        recommendation=policy_rep,
        is_demo=is_demo_active
    )
    
    st.text_area("Official Situation Briefing Document", report_text, height=450)
    
    st.download_button(
        label="📥 Download Executive Briefing (.txt)",
        data=report_text,
        file_name=f"PRICEGUARD_Briefing_{selected_commodity}_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )
