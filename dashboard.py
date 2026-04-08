import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time

from environment import TrafficLightEnv
from action import TrafficLightAction

# --- CONFIGURATION & THEME ---
THEME = {
    "bg": "#000000",
    "card": "#0a0a0a",
    "border": "#1e293b",
    "text": "#f8fafc",
    "accent": "#6366f1",
    "success": "#10b981",
    "danger": "#ef4444",
}

st.set_page_config(
    page_title="Traffic AI | JET BLACK",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Inter', sans-serif;
        background-color: {THEME["bg"]};
        color: {THEME["text"]};
    }}
    
    [data-testid="stHeader"] {{ background: transparent; }}
    [data-testid="stSidebar"] {{ background-color: #050505; border-right: 1px solid {THEME["border"]}; }}

    /* Cards */
    .pro-card {{
        background-color: {THEME["card"]};
        border-radius: 8px;
        border: 1px solid {THEME["border"]};
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }}

    .label {{
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 8px;
    }}

    /* Buttons */
    div.stButton > button {{
        background-color: #050505 !important;
        border: 1px solid {THEME["border"]} !important;
        color: {THEME["text"]} !important;
        border-radius: 4px !important;
        font-weight: 500 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    div.stButton > button:hover {{
        border-color: {THEME["accent"]} !important;
        background-color: rgba(99, 102, 241, 0.1) !important;
        color: {THEME["accent"]} !important;
    }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{ font-weight: 700; color: #fff; }}
    
    /* Audit Log Table */
    .stDataFrame {{ border: 1px solid {THEME["border"]} !important; border-radius: 4px; }}
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
    old_total = st.session_state.obs.north_cars + st.session_state.obs.south_cars + st.session_state.obs.east_cars + st.session_state.obs.west_cars
    
    action = TrafficLightAction(road=road_name)
    obs = st.session_state.env.step(action)
    st.session_state.obs = obs
    
    new_total = obs.north_cars + obs.south_cars + obs.east_cars + obs.west_cars
    reward = getattr(obs, 'reward', 0.0)
    st.session_state.total_reward += reward
    
    st.session_state.telemetry.append({
        "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
        "step": st.session_state.env._state.step_count,
        "action": road_name.upper(),
        "reward": reward,
        "load_delta": new_total - old_total,
        "current_total": new_total
    })

def reset_env():
    st.session_state.obs = st.session_state.env.reset()
    st.session_state.telemetry = []
    st.session_state.total_reward = 0.0

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown(f"<h2 style='color: {THEME["accent"]};'>TRAFFIC AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.8rem; color: #475569;'>ENTERPRISE v2.5.0 // JET BLACK</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("📊 Real-time Dashboard", use_container_width=True):
        st.session_state.current_page = "Dashboard"
    if st.button("🏗 Environment Config", use_container_width=True):
        st.session_state.current_page = "Config"
    if st.button("📔 Full Audit Logs", use_container_width=True):
        st.session_state.current_page = "Logs"
        
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    if st.button("🔄 HARD SYSTEM RESET", type="primary", use_container_width=True):
        reset_env()
        st.rerun()

# --- PAGE ROUTING ---

if st.session_state.current_page == "Dashboard":
    # --- DASHBOARD HEADER ---
    h_col1, h_col2 = st.columns([2, 1])
    with h_col1:
        st.title("Operational Dashboard")
    with h_col2:
        st.markdown(f"<div style='text-align: right; color: {THEME["success"]}; font-weight: 600;'>● 4 NODES ONLINE</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: right; color: #475569; font-size: 0.7rem;'>ID: {st.session_state.env._state.episode_id[:20]}</div>", unsafe_allow_html=True)

    st.markdown("<hr style='border: 0.5px solid #111; margin: 20px 0;'>", unsafe_allow_html=True)

    # --- TOP METRICS ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Reward", f"{st.session_state.total_reward:.2f}")
    with m2:
        total_cars = st.session_state.obs.north_cars + st.session_state.obs.south_cars + st.session_state.obs.east_cars + st.session_state.obs.west_cars
        st.metric("Network Load", f"{total_cars} Units")
    with m3:
        st.metric("System Cycle", st.session_state.env._state.step_count)
    with m4:
        last_rew = st.session_state.telemetry[-1]['reward'] if st.session_state.telemetry else 0.0
        st.metric("Last Reward", f"{last_rew:.2f}")

    # --- MAIN VISUALS ---
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
        st.markdown("<div class='label'>Network Topology Analysis</div>", unsafe_allow_html=True)
        
        # Intersection Visual
        v1, v2, v3 = st.columns([1,1,1])
        with v2:
            is_g = st.session_state.obs.current_green == "north"
            st.markdown(f"<div style='text-align: center; border: 1px solid #111; padding: 15px; border-radius: 8px;'><div style='color: {'#10b981' if is_g else '#ef4444'}; font-size: 1.5rem;'>●</div><div>NORTH</div><div style='font-size: 1.2rem; font-weight: 700;'>{st.session_state.obs.north_cars}</div></div>", unsafe_allow_html=True)
        
        v4, v5, v6 = st.columns([1,1,1])
        with v4:
            is_g = st.session_state.obs.current_green == "west"
            st.markdown(f"<div style='text-align: center; border: 1px solid #111; padding: 15px; border-radius: 8px;'><div style='color: {'#10b981' if is_g else '#ef4444'}; font-size: 1.5rem;'>●</div><div>WEST</div><div style='font-size: 1.2rem; font-weight: 700;'>{st.session_state.obs.west_cars}</div></div>", unsafe_allow_html=True)
        with v5:
            st.markdown("<div style='height: 100px; display: flex; align-items: center; justify-content: center;'><div style='width: 40px; height: 40px; border: 2px solid #333; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: #050505;'><div style='width: 8px; height: 8px; background: #6366f1; border-radius: 50%; box-shadow: 0 0 10px #6366f1;'></div></div></div>", unsafe_allow_html=True)
        with v6:
            is_g = st.session_state.obs.current_green == "east"
            st.markdown(f"<div style='text-align: center; border: 1px solid #111; padding: 15px; border-radius: 8px;'><div style='color: {'#10b981' if is_g else '#ef4444'}; font-size: 1.5rem;'>●</div><div>EAST</div><div style='font-size: 1.2rem; font-weight: 700;'>{st.session_state.obs.east_cars}</div></div>", unsafe_allow_html=True)
            
        v7, v8, v9 = st.columns([1,1,1])
        with v8:
            is_g = st.session_state.obs.current_green == "south"
            st.markdown(f"<div style='text-align: center; border: 1px solid #111; padding: 15px; border-radius: 8px;'><div style='color: {'#10b981' if is_g else '#ef4444'}; font-size: 1.5rem;'>●</div><div>SOUTH</div><div style='font-size: 1.2rem; font-weight: 700;'>{st.session_state.obs.south_cars}</div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c_right:
        st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
        st.markdown("<div class='label'>Manual Intervention</div>", unsafe_allow_html=True)
        if st.button("ACTIVATE NORTH [G]"): perform_action("north")
        if st.button("ACTIVATE SOUTH [G]"): perform_action("south")
        if st.button("ACTIVATE EAST [G]"): perform_action("east")
        if st.button("ACTIVATE WEST [G]"): perform_action("west")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
        st.markdown("<div class='label'>Load Distribution</div>", unsafe_allow_html=True)
        data = pd.DataFrame({"Node": ["N", "S", "E", "W"], "Load": [st.session_state.obs.north_cars, st.session_state.obs.south_cars, st.session_state.obs.east_cars, st.session_state.obs.west_cars]})
        fig = px.bar(data, x="Node", y="Load", template="plotly_dark", color_discrete_sequence=[THEME["accent"]], height=180)
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    # --- BOTTOM TELEMETRY ---
    st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Live Telemetry Stream</div>", unsafe_allow_html=True)
    if st.session_state.telemetry:
        df_log = pd.DataFrame(st.session_state.telemetry).tail(5)[::-1]
        st.table(df_log[["timestamp", "action", "reward", "current_total"]])
    else:
        st.info("Waiting for system activation...")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.current_page == "Config":
    st.title("Environment Configuration")
    st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Hardware Simulation Parameters</div>", unsafe_allow_html=True)
    st.write("Current simulation running at **Full Fidelity**.")
    st.slider("Traffic Density Scaling", 0.0, 2.0, 1.0)
    st.checkbox("Enable Stochastic Turbulence", value=True)
    st.checkbox("Autonomous Agent Handover", value=False)
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.current_page == "Logs":
    st.title("System Audit Logs")
    st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Full Session Telemetry History</div>", unsafe_allow_html=True)
    if st.session_state.telemetry:
        st.dataframe(pd.DataFrame(st.session_state.telemetry), use_container_width=True)
    else:
        st.warning("No audit logs recorded for this session.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<div style='text-align: center; opacity: 0.1; font-size: 0.6rem; margin-top: 50px;'>JET BLACK ENTERPRISE // (C) 2026 TRAFFIC CORE</div>", unsafe_allow_html=True)
