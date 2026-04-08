---
title: Traffic Light Controller RL Environment
sdk: docker
app_port: 7860
---

# Traffic Light Controller System

This project is a small reinforcement learning environment for a 4-road traffic intersection.

An AI agent chooses which road gets the green light:
- `north`
- `south`
- `east`
- `west`

The environment is built with:
- Python
- FastAPI
- OpenEnv
- Pydantic

It is designed to be:
- easy to understand for beginners
- runnable locally with `uvicorn`
- deployable to Hugging Face Spaces with Docker

## Project Files

- `action.py` defines the action space
- `observation.py` defines the observation schema
- `environment.py` contains the traffic simulation logic
- `application.py` starts the FastAPI + OpenEnv server
- `dashboard.py` is the premium Streamlit UI (Stitch-inspired)
- `inference.py` is a simple client that runs 10 steps
- `requirements.txt` lists Python packages
- `Dockerfile` is optimized for Streamlit + Hugging Face Spaces

## How the Environment Works

### Reset

When you call `reset()`:
- each road starts with a random number of cars from 1 to 10
- the default green light is `north`
- an observation is returned

### Step

When you call `step(action)`:
- the selected road becomes green
- 1 to 3 cars leave from that road
- 0 to 2 new cars arrive on every road
- reward is calculated from the total number of cars:
  - total decreased -> `1.0`
  - total stayed the same -> `0.5`
  - total increased -> `0.0`

## Local Setup

### 1. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the server

```bash
uvicorn application:app --reload --host 127.0.0.1 --port 8000
```

Open these URLs in your browser:
- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/openenv/docs`

### 4. Run the inference client

Open a second terminal and run:

```bash
python inference.py
```

## Step-by-Step Terminal Commands

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn application:app --reload --host 127.0.0.1 --port 8000
```

In a second PowerShell window:

```powershell
.venv\Scripts\Activate.ps1
python inference.py
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn application:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal:

```bash
source .venv/bin/activate
python inference.py
```

## Example API Usage

### Reset the environment

```bash
curl -X POST http://127.0.0.1:8000/openenv/reset -H "Content-Type: application/json" -d "{}"
```

Example response:

```json
{
  "observation": {
    "reward": 0.0,
    "done": false,
    "north_cars": 6,
    "south_cars": 4,
    "east_cars": 8,
    "west_cars": 2,
    "current_green": "north"
  },
  "reward": 0.0,
  "done": false
}
```

### Step the environment

```bash
curl -X POST http://127.0.0.1:8000/openenv/step -H "Content-Type: application/json" -d "{\"action\": {\"road\": \"east\"}}"
```

Example response:

```json
{
  "observation": {
    "reward": 1.0,
    "done": false,
    "north_cars": 7,
    "south_cars": 4,
    "east_cars": 6,
    "west_cars": 3,
    "current_green": "east"
  },
  "reward": 1.0,
  "done": false
}
```

### PowerShell API examples

Reset:

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/openenv/reset" -ContentType "application/json" -Body "{}"
```

Step:

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/openenv/step" -ContentType "application/json" -Body '{"action":{"road":"west"}}'
```

## How to Test

### Manual test

1. Start the server.
2. Open `http://127.0.0.1:8000/openenv/docs`.
3. Try `POST /reset`.
4. Then try `POST /step` with a road like `north`.

### Script test

Run:

```bash
python inference.py
```

The script:
- resets the environment
- finds the road with the most cars
- sends that action to the server
- repeats for 10 steps

## Hugging Face Spaces Deployment

This repository is already Docker-ready.

### Option 1: Upload through the Hugging Face website

1. Create a new Space on Hugging Face.
2. Choose `Docker` as the Space SDK.
3. Upload all project files.
4. Hugging Face will build the Docker image using the `Dockerfile`.

### Option 2: Push with git

```bash
git init
git add .
git commit -m "Initial traffic light OpenEnv project"
git branch -M main
git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
git push -u origin main
```

### Why the README has a small header block

The `README.md` starts with:
- `sdk: docker`
- `app_port: 7860`

That helps Hugging Face Spaces understand how to run the project.

## Important Beginner Note About OpenEnv

OpenEnv's plain HTTP reset and step routes create the environment from a factory on each request.

For this beginner project, `application.py` uses one shared `TrafficLightEnv` instance so the episode state is preserved between:
- `/openenv/reset`
- `/openenv/step`

That keeps the demo simple and makes the API feel like a normal RL environment.

## Common Errors and Fixes

### Error: `ModuleNotFoundError`

Cause:
- dependencies are not installed
- virtual environment is not active

Fix:

```bash
pip install -r requirements.txt
```

### Error: `uvicorn` command not found

Fix:

```bash
python -m uvicorn application:app --reload --host 127.0.0.1 --port 8000
```

### Error: PowerShell says scripts are disabled

Fix:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

### Error: Port 8000 is already in use

Run the server on a different port:

```bash
uvicorn application:app --reload --host 127.0.0.1 --port 8001
```

If you do that, also update `BASE_URL` in `inference.py`.

### Error: Step called before reset

The environment handles this automatically, but it is still best practice to call:

1. `/openenv/reset`
2. `/openenv/step`

## Next Ideas

Once this beginner version works, you can extend it with:
- yellow lights
- episode ending conditions
- time-based rewards
- real RL training instead of a rule-based inference script
