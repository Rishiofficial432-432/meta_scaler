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


app = FastAPI(
    title="Traffic Light Controller System",
    description="A beginner-friendly FastAPI + OpenEnv reinforcement learning demo.",
)

# Register /reset and /step directly on the root app so the checker can reach them.
openenv_server = HTTPEnvServer(
    env=get_shared_environment,
    action_cls=TrafficLightAction,
    observation_cls=TrafficLightObservation,
)
openenv_server.register_routes(app)


@app.get("/")
def read_root() -> dict:
    """Small helper endpoint for anyone opening the server in a browser."""
    return {
        "message": "Traffic Light Controller System is running.",
        "openenv_reset": "/reset",
        "openenv_step": "/step",
        "openenv_docs": "/docs",
    }
