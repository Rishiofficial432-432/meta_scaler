from pydantic import Field
from openenv.core.env_server import Observation

from action import RoadName


class TrafficLightObservation(Observation):
    """Observation returned after reset() and step()."""

    north_cars: int = Field(..., ge=0, description="Number of cars waiting on the north road.")
    south_cars: int = Field(..., ge=0, description="Number of cars waiting on the south road.")
    east_cars: int = Field(..., ge=0, description="Number of cars waiting on the east road.")
    west_cars: int = Field(..., ge=0, description="Number of cars waiting on the west road.")
    current_green: RoadName = Field(
        ...,
        description="Road that currently has the green light.",
    )
