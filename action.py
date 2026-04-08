from typing import Literal

from pydantic import Field
from openenv.core.env_server import Action

# These are the only roads the agent is allowed to choose.
RoadName = Literal["north", "south", "east", "west"]


class TrafficLightAction(Action):
    """Action sent by the agent to the environment."""

    road: RoadName = Field(
        ...,
        description="Road that should get the green light for this step.",
    )
