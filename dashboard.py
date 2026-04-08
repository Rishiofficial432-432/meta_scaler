import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

from environment import TrafficLightEnv
from action import TrafficLightAction

# --- CONFIGURATION ---
THEME = {
    "bg": "#0f172a",
    "card": "#1e293b",
    "border": "#334155",
    "text": "#f8fafc",
    "accent": "#6366f1",
    "success": "#10b981",
    "danger": "#ef4444",
    "warning": "#f59e0b"
}

st.set_page_config(
    page_title="Traffic AI | Enterprise Interface",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ADVANCED CSS ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Inter', sans-serif;
        background-color: {THEME["bg"]};
        color: {THEME["text"]};
    }}

    /* Professional Dashboard Cards */
    .pro-card {{
        background-color: {THEME["card"]};
        border-radius: 8px;
        border: 1px solid {THEME["border"]};
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
    }}

    /* Refined Typography */
    h1, h2, h3, h4 {{
        font-weight: 700 !important;
        letter-spacing: -0.025em;
        margin: 0 !important;
    }}
    
    .label {{
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 8px;
    }}

    /* Buttons */
    div.stButton > button {{
        background-color: #1e293b !important;
        border: 1px solid {THEME["border"]} !important;
        color: {THEME["text"]} !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease;
    }}
    div.stButton > button:hover {{
        border-color: {THEME["accent"]} !important;
        background-color: {THEME["accent"]} !important;
        color: white !important;
    }}

    /* Metric Styling */
    [data-testid="stMetricValue"] {{
        font-weight: 700;
        color: {THEME["text"]};
    }}
    
    /* Scrollbar */
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: {THEME["bg"]}; }}
    ::-webkit-scrollbar-thumb {{ background: {THEME["border"]}; border-radius: 10px; }}
</style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if "env" not in st.session_state:
    st.session_state.env = TrafficLightEnv()
    st.session_state.obs = st.session_state.env.reset()
    st.session_state.telemetry = []
    st.session_state.total_reward = 0.0
    st.session_state.current_page = "Dashboard"

def perform_action(road_name):
    # Pre-action stats
    before_cars = {
        "north": st.session_state.obs.north_cars,
        "south": st.session_state.obs.south_cars,
        "east": st.session_state.obs.east_cars,
        "west": st.session_state.obs.west_cars
    }
    
    action = TrafficLightAction(road=road_name)
    obs = st.session_state.env.step(action)
    st.session_state.obs = obs
    
    reward = getattr(obs, 'reward', 0.0)
    st.session_state.total_reward += reward
    
    # Telemetry data
    st.session_state.telemetry.append({
        "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
        "step": st.session_state.env._state.step_count,
        "transition": f"{road_name.upper()}",
        "reward": reward,
        "load_before": sum(before_cars.values()),
        "load_after": obs.north_cars + obs.south_cars + obs.east_cars + obs.west_cars
    })

def reset_simulation():
    st.session_state.obs = st.session_state.env.reset()
    st.session_state.telemetry = []
    st.session_state.total_reward = 0.0

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/traffic-light.png", width=80)
    st.markdown("<h2 style='margin-bottom: 20px;'>TRAFFIC CORE AI</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.button("📊 Dashboard", use_container_width=True): pass
    if st.button("🏗 Environment Config", use_container_width=True): pass
    if st.button("📔 Audit Logs", use_container_width=True): pass
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.info("System Version: 2.1.0-ENT\nStatus: Operational")
    
    if st.button("⚠ System Restart", type="secondary", use_container_width=True):
        reset_simulation()
        st.rerun()

# --- TOP NAVIGATION BAR ---
nav_col1, nav_col2, nav_col3 = st.columns([2, 1, 1])
with nav_col1:
    st.markdown("<h1 style='font-size: 1.5rem;'>Operational Dashboard <span style='font-weight: 300; opacity: 0.5;'>/ Traffic Control</span></h1>", unsafe_allow_html=True)

with nav_col2:
    st.markdown(f"""
    <div style='background: #1e293b; border: 1px solid #334155; border-radius: 4px; padding: 4px 12px; font-size: 0.8rem; text-align: center;'>
        Session ID: <span style='color: {THEME["accent"]};'>{st.session_state.env._state.episode_id[:16]}</span>
    </div>
    """, unsafe_allow_html=True)

with nav_col3:
    st.markdown(f"""
    <div style='text-align: right;'>
        <span style='background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid #10b981; border-radius: 20px; padding: 2px 12px; font-size: 0.7rem; font-weight: 700;'>LIVE TELEMETRY</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- MAIN CONTENT ---
col_stats, col_viz, col_control = st.columns([1, 2, 1])

# Column 1: Core Performance Metrics
with col_stats:
    st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Session Efficiency</div>", unsafe_allow_html=True)
    st.metric("Aggregate Reward", f"{st.session_state.total_reward:.2f}", 
              delta=f"{st.session_state.telemetry[-1]['reward']:.2f}" if st.session_state.telemetry else None)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Network Utilization</div>", unsafe_allow_html=True)
    total_cars = st.session_state.obs.north_cars + st.session_state.obs.south_cars + st.session_state.obs.east_cars + st.session_state.obs.west_cars
    st.metric("Active Load", f"{total_cars} Units", delta=f"{st.session_state.telemetry[-1]['load_after'] - st.session_state.telemetry[-1]['load_before']}" if st.session_state.telemetry else None, delta_color="inverse")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='label'>System Steps</div>", unsafe_allow_html=True)
    st.metric("Cycle Count", st.session_state.env._state.step_count)
    st.markdown("</div>", unsafe_allow_html=True)

# Column 2: Intersection Real-time Visualizer
with col_viz:
    st.markdown("<div class='pro-card' style='height: 100%; border-color: #475569;'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Network State Visualization</div>", unsafe_allow_html=True)
    
    # Grid layout for intersection
    v1, v2, v3 = st.columns([1, 1, 1])
    with v2:
        is_g = st.session_state.obs.current_green == "north"
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: {"rgba(16, 185, 129, 0.05)" if is_g else "transparent"}; border-radius: 8px;'>
            <div style='color: {"#10b981" if is_g else "#ef4444"}; font-size: 1.5rem;'>{'●' if is_g else '○'}</div>
            <div style='font-size: 0.8rem; font-weight: 600;'>NORTH</div>
            <div style='font-size: 1.2rem;'>{st.session_state.obs.north_cars} V</div>
        </div>
        """, unsafe_allow_html=True)
    
    v4, v5, v6 = st.columns([1, 1, 1])
    with v4:
        is_g = st.session_state.obs.current_green == "west"
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: {"rgba(16, 185, 129, 0.05)" if is_g else "transparent"}; border-radius: 8px;'>
            <div style='color: {"#10b981" if is_g else "#ef4444"}; font-size: 1.5rem;'>{'●' if is_g else '○'}</div>
            <div style='font-size: 0.8rem; font-weight: 600;'>WEST</div>
            <div style='font-size: 1.2rem;'>{st.session_state.obs.west_cars} V</div>
        </div>
        """, unsafe_allow_html=True)
    with v5:
        st.markdown(f"""
        <div style='height: 100px; display: flex; align-items: center; justify-content: center;'>
            <div style='border: 4px solid {THEME["border"]}; border-radius: 50%; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; background: #0f172a;'>
                <div style='width: 10px; height: 10px; background: {THEME["accent"]}; border-radius: 50%; box-shadow: 0 0 10px {THEME["accent"]};'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with v6:
        is_g = st.session_state.obs.current_green == "east"
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: {"rgba(16, 185, 129, 0.05)" if is_g else "transparent"}; border-radius: 8px;'>
            <div style='color: {"#10b981" if is_g else "#ef4444"}; font-size: 1.5rem;'>{'●' if is_g else '○'}</div>
            <div style='font-size: 0.8rem; font-weight: 600;'>EAST</div>
            <div style='font-size: 1.2rem;'>{st.session_state.obs.east_cars} V</div>
        </div>
        """, unsafe_allow_html=True)
        
    v7, v8, v9 = st.columns([1, 1, 1])
    with v8:
        is_g = st.session_state.obs.current_green == "south"
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: {"rgba(16, 185, 129, 0.05)" if is_g else "transparent"}; border-radius: 8px;'>
            <div style='color: {"#10b981" if is_g else "#ef4444"}; font-size: 1.5rem;'>{'●' if is_g else '○'}</div>
            <div style='font-size: 0.8rem; font-weight: 600;'>SOUTH</div>
            <div style='font-size: 1.2rem;'>{st.session_state.obs.south_cars} V</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Column 3: Manual Override & Control
with col_control:
    st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Manual Override Units</div>", unsafe_allow_html=True)
    if st.button("SET NORTH GATE G-1", use_container_width=True): perform_action("north")
    if st.button("SET SOUTH GATE G-2", use_container_width=True): perform_action("south")
    if st.button("SET EAST GATE G-3", use_container_width=True): perform_action("east")
    if st.button("SET WEST GATE G-4", use_container_width=True): perform_action("west")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>System Health Analytics</div>", unsafe_allow_html=True)
    # Simple Bar chart for distribution
    dist = pd.DataFrame({
        "Road": ["N", "S", "E", "W"],
        "Cars": [st.session_state.obs.north_cars, st.session_state.obs.south_cars, st.session_state.obs.east_cars, st.session_state.obs.west_cars]
    })
    fig_dist = px.bar(dist, x="Road", y="Cars", color="Cars", height=150, template="plotly_dark", color_continuous_scale="Viridis")
    fig_dist.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False)
    st.plotly_chart(fig_dist, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# --- SYSTEM TELEMETRY LOG ---
st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
st.markdown("<div class='label'>System Telemetry Audit Log</div>", unsafe_allow_html=True)
if st.session_state.telemetry:
    telemetry_df = pd.DataFrame(st.session_state.telemetry).tail(8)[::-1]
    st.dataframe(telemetry_df, use_container_width=True, hide_index=True)
else:
    st.info("System initialized. Awaiting first telemetry packet...")
st.markdown("</div>", unsafe_allow_html=True)

# --- CHARTING ---
if st.session_state.telemetry:
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
        st.markdown("<div class='label'>Reward Progression Convergence</div>", unsafe_allow_html=True)
        fig_rew = px.line(pd.DataFrame(st.session_state.telemetry), x="step", y="reward", template="plotly_dark", color_discrete_sequence=[THEME["accent"]])
        fig_rew.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_rew, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with chart_col2:
        st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
        st.markdown("<div class='label'>Network Load Balancing</div>", unsafe_allow_html=True)
        fig_load = px.area(pd.DataFrame(st.session_state.telemetry), x="step", y="load_after", template="plotly_dark", color_discrete_sequence=[THEME["success"]])
        fig_load.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_load, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"""
<div style='text-align: center; opacity: 0.3; font-size: 0.7rem; margin-top: 50px; padding: 20px 0; border-top: 1px solid {THEME["border"]};'>
    OFFICIAL ENTERPRISE RELEASE // BUILD 21.0.4.ENT // ENCRYPTION AES-256 ACTIVE
</div>
""", unsafe_allow_html=True)
