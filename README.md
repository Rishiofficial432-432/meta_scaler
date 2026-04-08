---
title: Traffic AI v2.0
emoji: 🚦
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: true
---

# 🚦 Traffic AI v2.1.0 Enterprise

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A professional, enterprise-grade reinforcement learning dashboard for a 4-way traffic light controller. Built with **OpenEnv**, **FastAPI**, and **Streamlit**, this project features high-density telemetry, a deep-slate professional theme, and robust audit logging.

![Dashboard Preview](https://raw.githubusercontent.com/Rishiofficial432-432/meta_scaler/main/assets/dashboard_preview.png)

## ✨ Key Features

- **Premium Design System**: Sleek dark mode, glassmorphism, and neon accents for a high-tech feel.
- **Real-Time Visualization**: Interactive 4-road intersection grid reflecting the live AI environment state.
- **Reinforcement Learning**: Powered by the OpenEnv framework for robust simulation and training.
- **Dual API/UI Support**: Choose between the raw FastAPI endpoint or the premium Streamlit dashboard.
- **Hugging Face Ready**: Fully optimized Docker configuration for instant deployment to Hugging Face Spaces.

## 🚀 Quick Start

### Local Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Rishiofficial432-432/meta_scaler.git
   cd meta_scaler
   ```

2. **Setup virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Dashboard

Launch the premium Streamlit interface:
```bash
streamlit run dashboard.py
```

### Running the API Server

Launch the FastAPI + OpenEnv backend:
```bash
uvicorn application:app --reload --host 127.0.0.1 --port 8000
```

## 🏗 Project Structure

- `dashboard.py`: Premium Streamlit UI implementation.
- `environment.py`: Core Traffic Light RL Environment logic.
- `action.py` & `observation.py`: OpenEnv schema definitions.
- `application.py`: FastAPI server for API-based interaction.
- `Dockerfile`: Deployment-ready configuration for Hugging Face.

## 🌍 Deployment

### Hugging Face Spaces
This repository is optimized for Hugging Face Spaces using **Docker**. Simply upload the files to a new Space and it will automatically build and launch the Streamlit dashboard on port 7860.

## 📄 License
Distributed under the MIT License. See `README.md` for more information.

---
Built with 💙 by Traffic AI Team.
