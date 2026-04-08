import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time

from environment import TrafficLightEnv
from action import TrafficLightAction

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Traffic AI v2.0 Dashboard",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Main Background and Text */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Premium Glassmorphism Cards */
    .glass-card {
        background: rgba(23, 28, 36, 0.7);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    
    /* Neon Accents */
    .neon-green {
        color: #39ff14;
        text-shadow: 0 0 10px #39ff14;
    }
    .neon-red {
        color: #ff3131;
        text-shadow: 0 0 10px #ff3131;
    }
    .neon-blue {
        color: #00f3ff;
        text-shadow: 0 0 10px #00f3ff;
    }
    
    /* Custom Buttons - Cyberpunk Style */
    div.stButton > button {
        width: 100%;
        background-color: transparent !important;
        border: 2px solid #00f3ff !important;
        color: #00f3ff !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        text-transform: uppercase;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #00f3ff !important;
        color: #000 !important;
        box-shadow: 0 0 15px #00f3ff;
    }
    
    /* Reset Button Special Styling */
    .reset-btn div.stButton > button {
        border-color: #ff3131 !important;
        color: #ff3131 !important;
    }
    .reset-btn div.stButton > button:hover {
        background-color: #ff3131 !important;
        color: #fff !important;
        box-shadow: 0 0 15px #ff3131;
    }

    /* Direction Indicators */
    .dir-indicator {
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE ENVIRONMENT ---
if "env" not in st.session_state:
    st.session_state.env = TrafficLightEnv()
    st.session_state.obs = st.session_state.env.reset()
    st.session_state.history = []
    st.session_state.total_reward = 0.0

def step_env(road_name):
    action = TrafficLightAction(road=road_name)
    obs = st.session_state.env.step(action)
    st.session_state.obs = obs
    reward = getattr(obs, 'reward', 0.0)
    st.session_state.total_reward += reward
    
    st.session_state.history.append({
        "step": st.session_state.env._state.step_count,
        "action": road_name,
        "reward": reward,
        "total_cars": obs.north_cars + obs.south_cars + obs.east_cars + obs.west_cars,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

def reset_env():
    st.session_state.obs = st.session_state.env.reset()
    st.session_state.history = []
    st.session_state.total_reward = 0.0

# --- HEADER ---
st.markdown("""
<div style='display: flex; justify-content: space-between; align-items: center;'>
    <h1 class='neon-blue' style='margin:0;'>TRAFFIC AI <span style='font-size: 0.5em; opacity: 0.7;'>v2.0</span></h1>
    <div class='glass-card' style='padding: 10px 20px; margin: 0;'>
        Status: <span class='neon-green'>Active</span> | Episode: <span class='neon-blue'>{}</span>
    </div>
</div>
<hr style='border: 1px solid rgba(255,255,255,0.1); margin: 20px 0;'>
""".format(st.session_state.env._state.episode_id[:8]), unsafe_allow_html=True)

# --- MAIN LAYOUT ---
col1, col2 = st.columns([1.5, 1])

with col1:
    # Intersection Visualization
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Intersection Real-time View</h3>", unsafe_allow_html=True)
    
    # We create a 3x3 grid for the intersection
    # [Empty, North, Empty]
    # [West, Center, East]
    # [Empty, South, Empty]
    
    grid1, grid2, grid3 = st.columns([1,1,1])
    
    with grid1:
        st.write("") # Empty
    with grid2:
        is_green = st.session_state.obs.current_green == "north"
        st.markdown(f"""
        <div class='dir-indicator'>NORTH</div>
        <div style='text-align:center; font-size: 2.5rem;' class='{"neon-green" if is_green else "neon-red"}'>
            {'●' if is_green else '○'}
        </div>
        <div style='text-align:center; font-size: 1.5rem;'>{st.session_state.obs.north_cars} Cars</div>
        """, unsafe_allow_html=True)
    with grid3:
        st.write("") # Empty
        
    grid4, grid5, grid6 = st.columns([1,1,1])
    with grid4:
        is_green = st.session_state.obs.current_green == "west"
        st.markdown(f"""
        <div class='dir-indicator'>WEST</div>
        <div style='text-align:center; font-size: 2.5rem;' class='{"neon-green" if is_green else "neon-red"}'>
            {'●' if is_green else '○'}
        </div>
        <div style='text-align:center; font-size: 1.5rem;'>{st.session_state.obs.west_cars} Cars</div>
        """, unsafe_allow_html=True)
    with grid5:
        # Central Hub
        st.markdown("""
        <div style='background: #1f2937; border-radius: 50%; width: 100px; height: 100px; margin: auto; display: flex; align-items: center; justify-content: center; border: 2px solid #374151;'>
            <span style='font-size: 2rem;'>🚦</span>
        </div>
        """, unsafe_allow_html=True)
    with grid6:
        is_green = st.session_state.obs.current_green == "east"
        st.markdown(f"""
        <div class='dir-indicator'>EAST</div>
        <div style='text-align:center; font-size: 2.5rem;' class='{"neon-green" if is_green else "neon-red"}'>
            {'●' if is_green else '○'}
        </div>
        <div style='text-align:center; font-size: 1.5rem;'>{st.session_state.obs.east_cars} Cars</div>
        """, unsafe_allow_html=True)

    grid7, grid8, grid9 = st.columns([1,1,1])
    with grid7:
        st.write("") # Empty
    with grid8:
        is_green = st.session_state.obs.current_green == "south"
        st.markdown(f"""
        <div class='dir-indicator'>SOUTH</div>
        <div style='text-align:center; font-size: 2.5rem;' class='{"neon-green" if is_green else "neon-red"}'>
            {'●' if is_green else '○'}
        </div>
        <div style='text-align:center; font-size: 1.5rem;'>{st.session_state.obs.south_cars} Cars</div>
        """, unsafe_allow_html=True)
    with grid9:
        st.write("") # Empty
        
    st.markdown("</div>", unsafe_allow_html=True)

    # Manual Controls
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom: 20px;'>Manual Traffic Control</h3>", unsafe_allow_html=True)
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)
    with ctrl_col1:
        if st.button("Set North Green"): step_env("north")
    with ctrl_col2:
        if st.button("Set South Green"): step_env("south")
    with ctrl_col3:
        if st.button("Set East Green"): step_env("east")
    with ctrl_col4:
        if st.button("Set West Green"): step_env("west")
    
    st.markdown("<div style='margin-top: 20px;' class='reset-btn'>", unsafe_allow_html=True)
    if st.button("Reset Environment"): reset_env()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    # Stats & History
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3>Environment Stats</h3>", unsafe_allow_html=True)
    
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        st.metric("Total Reward", f"{st.session_state.total_reward:.1f}", delta=None)
        st.metric("Current Traffic", st.session_state.obs.north_cars + st.session_state.obs.south_cars + st.session_state.obs.east_cars + st.session_state.obs.west_cars)
    with s_col2:
        st.metric("Steps Taken", st.session_state.env._state.step_count)
        last_reward = st.session_state.history[-1]['reward'] if st.session_state.history else 0.0
        st.metric("Last Reward", f"{last_reward:.1f}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Reward Plot
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3>Reward History</h3>", unsafe_allow_html=True)
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        fig = px.line(df, x="step", y="reward", template="plotly_dark", 
                      markers=True, color_discrete_sequence=["#00f3ff"])
        fig.update_layout(
            margin=dict(l=0, r=0, t=20, b=0),
            height=200,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet. Perform an action to see the history.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Action Log
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3>Action Log</h3>", unsafe_allow_html=True)
    if st.session_state.history:
        log_df = pd.DataFrame(st.session_state.history).tail(5)[::-1]
        st.table(log_df[["timestamp", "action", "reward"]])
    else:
        st.info("Waiting for first action...")
    st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div style='text-align: center; opacity: 0.5; font-size: 0.8em; margin-top: 50px;'>
    Powered by OpenEnv & Stitch Design System | © 2026 Traffic AI
</div>
""", unsafe_allow_html=True)
