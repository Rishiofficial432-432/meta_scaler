from fastapi import FastAPI
from openenv.core.env_server import HTTPEnvServer

from action import TrafficLightAction
from environment import TrafficLightEnv
from observation import TrafficLightObservation

# We reuse one environment instance so HTTP reset/step calls share the same episode.
shared_environment = TrafficLightEnv()


def get_shared_environment() -> TrafficLightEnv:
    """OpenEnv expects a factory function, so we return the shared demo env."""
    return shared_environment


openenv_app = FastAPI(
    title="OpenEnv Traffic Light API",
    description="OpenEnv routes for the traffic light controller environment.",
)

openenv_server = HTTPEnvServer(
    env=get_shared_environment,
    action_cls=TrafficLightAction,
    observation_cls=TrafficLightObservation,
)
openenv_server.register_routes(openenv_app)

app = FastAPI(
    title="Traffic Light Controller System",
    description="A beginner-friendly FastAPI + OpenEnv reinforcement learning demo.",
)

# Mounting here makes the OpenEnv routes available at /openenv/reset and /openenv/step.
app.mount("/openenv", openenv_app)


@app.get("/")
def read_root() -> dict:
    """Small helper endpoint for anyone opening the server in a browser."""
    return {
        "message": "Traffic Light Controller System is running.",
        "openenv_reset": "/openenv/reset",
        "openenv_step": "/openenv/step",
        "openenv_docs": "/openenv/docs",
    }
