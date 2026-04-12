"""
Traffic Light Controller — OpenEnv Inference Script
=====================================================
Mandatory stdout format:
  [START] task=<task> env=<env> model=<model>
  [STEP]  step=<n> action=<action> reward=<0.00> done=<true|false> error=<msg|null>
  [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...>
"""

import os
from typing import List, Optional

import requests
from openai import OpenAI

# ── Configuration ────────────────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME",   "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN     = os.getenv("HF_TOKEN",     "")

# The running OpenEnv server (this same container on HF Spaces)
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://127.0.0.1:7860")

TASK_NAME  = "traffic-light-control"
BENCHMARK  = "traffic_light_openenv"
MAX_STEPS  = 10

SYSTEM_PROMPT = (
    "You control a 4-road traffic intersection. "
    "Each turn you must choose which road gets the green light. "
    "Respond with exactly one word — the road name: north, south, east, or west. "
    "Pick the road with the most cars waiting to maximise traffic flow."
)

# ── Logging helpers ───────────────────────────────────────────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    err = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} "
        f"done={str(done).lower()} error={err}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} "
        f"score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


# ── LLM action selection ──────────────────────────────────────────────────────

def choose_action(client: OpenAI, observation: dict) -> str:
    """Ask the LLM which road to give the green light."""
    user_msg = (
        f"Cars waiting — north: {observation['north_cars']}, "
        f"south: {observation['south_cars']}, "
        f"east: {observation['east_cars']}, "
        f"west: {observation['west_cars']}. "
        f"Current green: {observation['current_green']}. "
        "Which road should get the green light next?"
    )
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_msg},
            ],
            max_tokens=10,
            temperature=0.2,
        )
        raw = (resp.choices[0].message.content or "north").strip().lower()
        # Sanitise — keep only valid road names
        for road in ("north", "south", "east", "west"):
            if road in raw:
                return road
    except Exception:
        pass
    # Fallback: pick the road with the most cars
    counts = {
        "north": observation["north_cars"],
        "south": observation["south_cars"],
        "east":  observation["east_cars"],
        "west":  observation["west_cars"],
    }
    return max(counts, key=counts.get)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "no-key")

    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        # ── Reset ────────────────────────────────────────────────────────────
        reset_resp = requests.post(f"{ENV_BASE_URL}/reset", json={}, timeout=15)
        reset_resp.raise_for_status()
        data = reset_resp.json()
        observation = data.get("observation", data)

        for step in range(1, MAX_STEPS + 1):
            road = choose_action(client, observation)

            step_resp = requests.post(
                f"{ENV_BASE_URL}/step",
                json={"action": {"road": road}},
                timeout=15,
            )
            step_resp.raise_for_status()
            step_data = step_resp.json()

            observation = step_data.get("observation", step_data)
            reward = float(step_data.get("reward", 0.5))
            done   = bool(step_data.get("done", False))

            rewards.append(reward)
            steps_taken = step

            log_step(step=step, action=road, reward=reward, done=done, error=None)

            if done:
                break

        # Score = mean reward, clamped strictly inside (0, 1)
        if rewards:
            raw_score = sum(rewards) / len(rewards)
        else:
            raw_score = 0.5

        # Ensure strictly within (0, 1) — never exactly 0 or 1
        score = max(0.01, min(0.99, raw_score))
        success = score >= 0.5

    except Exception as exc:
        log_step(step=steps_taken + 1, action="error", reward=0.01, done=True, error=str(exc))
        score = 0.01
        success = False

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    main()
