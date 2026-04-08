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
    page_title="Traffic AI | CINEMATIC",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ADVANCED CSS WITH ANIMATIONS ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Keyframes */
    @keyframes slideUp {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    
    @keyframes pulseGlow {{
        0% {{ box-shadow: 0 0 5px rgba(99, 102, 241, 0.2); }}
        50% {{ box-shadow: 0 0 20px rgba(99, 102, 241, 0.6); }}
        100% {{ box-shadow: 0 0 5px rgba(99, 102, 241, 0.2); }}
    }}
    
    @keyframes greenPulse {{
        0% {{ opacity: 0.6; transform: scale(0.95); }}
        50% {{ opacity: 1; transform: scale(1.05); }}
        100% {{ opacity: 0.6; transform: scale(0.95); }}
    }}

    @keyframes shimmer {{
        0% {{ background-position: -200% 0; }}
        100% {{ background-position: 200% 0; }}
    }}

    /* Global Styles */
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Inter', sans-serif;
        background-color: {THEME["bg"]};
        color: {THEME["text"]};
    }}
    
    [data-testid="stHeader"] {{ background: transparent; }}
    [data-testid="stSidebar"] {{ 
        background-color: #050505; 
        border-right: 1px solid {THEME["border"]}; 
    }}

    /* Animated Containers */
    .animate-slide-up {{ animation: slideUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1); }}
    .animate-fade-in {{ animation: fadeIn 1.2s ease-out; }}
    
    .pro-card {{
        background-color: {THEME["card"]};
        border-radius: 12px;
        border: 1px solid {THEME["border"]};
        padding: 24px;
        margin-bottom: 24px;
        transition: all 0.3s ease;
    }}
    .pro-card:hover {{
        border-color: {THEME["accent"]};
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}

    .label {{
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #475569;
        margin-bottom: 12px;
    }}

    /* Specific Elements */
    .node-active {{
        border: 2px solid {THEME["success"]};
        background: rgba(16, 185, 129, 0.1);
        animation: pulseGlow 2s infinite;
    }}
    
    .light-green {{ color: {THEME["success"]}; animation: greenPulse 1.5s infinite; }}
    .light-red {{ color: {THEME["danger"]}; opacity: 0.3; }}

    /* Custom Buttons */
    div.stButton > button {{
        background: #0a0a0a !important;
        border: 1px solid #222 !important;
        color: #eee !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    div.stButton > button:hover {{
        border-color: {THEME["accent"]} !important;
        color: {THEME["accent"]} !important;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.3);
    }}

    /* Hide default decoration */
    [data-testid="stDecoration"] {{ display: none; }}
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

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"""
    <div class='animate-fade-in'>
        <h2 style='color: {THEME["accent"]}; margin-bottom: 0;'>TRAFFIC AI</h2>
        <p style='color: #475569; font-size: 0.7rem; letter-spacing: 0.1em;'>CINEMATIC v3.0 // JET BLACK</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("📊 Real-time Feed", use_container_width=True):
        st.session_state.current_page = "Dashboard"
    if st.button("🏗 Engine Config", use_container_width=True):
        st.session_state.current_page = "Config"
    if st.button("📔 Audit Vault", use_container_width=True):
        st.session_state.current_page = "Logs"
        
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    if st.button("⚡ REBOOT ENGINE", type="primary", use_container_width=True):
        reset_env()
        st.rerun()

# --- CONTENT ROUTING ---

if st.session_state.current_page == "Dashboard":
    # --- HEADER ---
    st.markdown(f"""
    <div class='animate-slide-up'>
        <div style='display: flex; justify-content: space-between; align-items: flex-end;'>
            <div>
                <h1 style='font-size: 2.2rem; font-weight: 800; margin-bottom: 0;'>Operational Feed</h1>
                <p style='color: #64748b;'>Unified Intersection Intelligence Node</p>
            </div>
            <div style='text-align: right;'>
                <div style='color: {THEME["success"]}; font-weight: 700; font-size: 0.8rem;'>● ENCRYPTION AES-256 ACTIVE</div>
                <div style='color: #475569; font-size: 0.6rem;'>SES: {st.session_state.env._state.episode_id[:24]}</div>
            </div>
        </div>
    </div>
    <hr style='border: 0.5px solid #111; margin: 20px 0;'>
    """, unsafe_allow_html=True)

    # --- TOP ANALYTICS ---
    st.markdown("<div class='animate-slide-up'>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Aggregate Reward", f"{st.session_state.total_reward:.2f}")
    with m2:
        total_cars = st.session_state.obs.north_cars + st.session_state.obs.south_cars + st.session_state.obs.east_cars + st.session_state.obs.west_cars
        st.metric("Current Throughput", f"{total_cars} Units")
    with m3:
        st.metric("Engine Cycle", st.session_state.env._state.step_count)
    with m4:
        last_rew = st.session_state.telemetry[-1]['reward'] if st.session_state.telemetry else 0.0
        st.metric("Instant Efficiency", f"{last_rew:.2f}")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- MAIN GRID ---
    col_viz, col_ctrl = st.columns([1.8, 1])
    
    with col_viz:
        st.markdown("<div class='pro-card animate-slide-up'>", unsafe_allow_html=True)
        st.markdown("<div class='label'>Network Topology Analysis</div>", unsafe_allow_html=True)
        
        # Grid visualizer
        v1, v2, v3 = st.columns([1,1,1])
        with v2:
            is_g = st.session_state.obs.current_green == "north"
            st.markdown(f"""
            <div style='text-align: center; border: 1px solid {"#333" if not is_g else THEME["success"]}; padding: 20px; border-radius: 12px; background: {"rgba(16, 185, 129, 0.05)" if is_g else "transparent"};'>
                <div class='{"light-green" if is_g else "light-red"}' style='font-size: 2rem;'>●</div>
                <div style='font-size: 0.7rem; font-weight: 700; color: #475569;'>NORTH</div>
                <div style='font-size: 1.5rem; font-weight: 800;'>{st.session_state.obs.north_cars} <span style='font-size: 0.6rem; font-weight: 400; color: #475569;'>V</span></div>
            </div>
            """, unsafe_allow_html=True)
        
        v4, v5, v6 = st.columns([1,1,1])
        with v4:
            is_g = st.session_state.obs.current_green == "west"
            st.markdown(f"""
            <div style='text-align: center; border: 1px solid {"#333" if not is_g else THEME["success"]}; padding: 20px; border-radius: 12px; background: {"rgba(16, 185, 129, 0.05)" if is_g else "transparent"};'>
                <div class='{"light-green" if is_g else "light-red"}' style='font-size: 2rem;'>●</div>
                <div style='font-size: 0.7rem; font-weight: 700; color: #475569;'>WEST</div>
                <div style='font-size: 1.5rem; font-weight: 800;'>{st.session_state.obs.west_cars} <span style='font-size: 0.6rem; font-weight: 400; color: #475569;'>V</span></div>
            </div>
            """, unsafe_allow_html=True)
        with v5:
            st.markdown(f"""
            <div style='height: 120px; display: flex; align-items: center; justify-content: center;'>
                <div style='width: 60px; height: 60px; border: 2px solid #111; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: #050505;'>
                    <div style='width: 12px; height: 12px; background: {THEME["accent"]}; border-radius: 50%; box-shadow: 0 0 15px {THEME["accent"]}; opacity: 0.8;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with v6:
            is_g = st.session_state.obs.current_green == "east"
            st.markdown(f"""
            <div style='text-align: center; border: 1px solid {"#333" if not is_g else THEME["success"]}; padding: 20px; border-radius: 12px; background: {"rgba(16, 185, 129, 0.05)" if is_g else "transparent"};'>
                <div class='{"light-green" if is_g else "light-red"}' style='font-size: 2rem;'>●</div>
                <div style='font-size: 0.7rem; font-weight: 700; color: #475569;'>EAST</div>
                <div style='font-size: 1.5rem; font-weight: 800;'>{st.session_state.obs.east_cars} <span style='font-size: 0.6rem; font-weight: 400; color: #475569;'>V</span></div>
            </div>
            """, unsafe_allow_html=True)
            
        v7, v8, v9 = st.columns([1,1,1])
        with v8:
            is_g = st.session_state.obs.current_green == "south"
            st.markdown(f"""
            <div style='text-align: center; border: 1px solid {"#333" if not is_g else THEME["success"]}; padding: 20px; border-radius: 12px; background: {"rgba(16, 185, 129, 0.05)" if is_g else "transparent"};'>
                <div class='{"light-green" if is_g else "light-red"}' style='font-size: 2rem;'>●</div>
                <div style='font-size: 0.7rem; font-weight: 700; color: #475569;'>SOUTH</div>
                <div style='font-size: 1.5rem; font-weight: 800;'>{st.session_state.obs.south_cars} <span style='font-size: 0.6rem; font-weight: 400; color: #475569;'>V</span></div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_ctrl:
        st.markdown("<div class='pro-card animate-slide-up' style='animation-delay: 0.1s;'>", unsafe_allow_html=True)
        st.markdown("<div class='label'>Manual Intervention Units</div>", unsafe_allow_html=True)
        if st.button("GATE ALPHA [N]"): perform_action("north")
        if st.button("GATE BRAVO [S]"): perform_action("south")
        if st.button("GATE CHARLIE [E]"): perform_action("east")
        if st.button("GATE DELTA [W]"): perform_action("west")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='pro-card animate-slide-up' style='animation-delay: 0.2s;'>", unsafe_allow_html=True)
        st.markdown("<div class='label'>Session Convergence</div>", unsafe_allow_html=True)
        if st.session_state.telemetry:
            df = pd.DataFrame(st.session_state.telemetry)
            fig = px.area(df, x="step", y="current_total", template="plotly_dark", color_discrete_sequence=[THEME["accent"]], height=180)
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_visible=False, yaxis_visible=False)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info(" telemetry awaiting...")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- BOTTOM LOG ---
    st.markdown("<div class='pro-card animate-slide-up' style='animation-delay: 0.3s;'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Live Telemetry Burst</div>", unsafe_allow_html=True)
    if st.session_state.telemetry:
        df_log = pd.DataFrame(st.session_state.telemetry).tail(3)[::-1]
        st.dataframe(df_log, use_container_width=True, hide_index=True)
    else:
        st.info("System initialized. Awaiting sensory input...")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.current_page == "Config":
    st.markdown("<div class='animate-fade-in'>", unsafe_allow_html=True)
    st.title("System Parameters")
    st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Simulation Physics</div>", unsafe_allow_html=True)
    st.slider("Atmospheric Friction", 0.0, 1.0, 0.4)
    st.slider("Node Discovery Latency", 0, 100, 14)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.current_page == "Logs":
    st.markdown("<div class='animate-fade-in'>", unsafe_allow_html=True)
    st.title("Audit Vault")
    st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Unified Telemetry Archive</div>", unsafe_allow_html=True)
    if st.session_state.telemetry:
        st.dataframe(pd.DataFrame(st.session_state.telemetry), use_container_width=True)
    else:
        st.warning("Vault is empty for current session.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown(f"""
<div style='text-align: center; opacity: 0.05; font-size: 0.5rem; margin-top: 100px; padding: 20px 0;'>
    SYSTEM BUILD 3.0.1-CINEMA // KERNEL v9.4 // (C) TRAFFIC CORE // JET BLACK
</div>
""", unsafe_allow_html=True)
