import random
from typing import Optional
from uuid import uuid4

from pydantic import Field
from openenv.core.env_server import Environment, State

from action import RoadName, TrafficLightAction
from observation import TrafficLightObservation


class TrafficLightState(State):
    """Internal state for the traffic intersection."""

    north_cars: int = Field(default=0, ge=0)
    south_cars: int = Field(default=0, ge=0)
    east_cars: int = Field(default=0, ge=0)
    west_cars: int = Field(default=0, ge=0)
    current_green: RoadName = Field(default="north")


class TrafficLightEnv(
    Environment[TrafficLightAction, TrafficLightObservation, TrafficLightState]
):
    """
    A small OpenEnv environment for a 4-road traffic light controller.

    We keep the logic intentionally simple so it is easy to learn from:
    - reset() creates a fresh random intersection
    - step() changes the green light and simulates cars leaving/arriving
    """

    def __init__(self) -> None:
        self._random = random.Random()
        self._state = TrafficLightState()

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs,
    ) -> TrafficLightObservation:
        """Start a new episode with random traffic on all four roads."""
        if seed is not None:
            self._random.seed(seed)

        self._state = TrafficLightState(
            episode_id=episode_id or str(uuid4()),
            step_count=0,
            north_cars=self._random.randint(1, 10),
            south_cars=self._random.randint(1, 10),
            east_cars=self._random.randint(1, 10),
            west_cars=self._random.randint(1, 10),
            current_green="north",
        )

        return self._build_observation(reward=0.0)

    def step(
        self,
        action: TrafficLightAction,
        timeout_s: Optional[float] = None,
        **kwargs,
    ) -> TrafficLightObservation:
        """
        Apply one action and return the next observation.

        Rules:
        - The selected road becomes green
        - 1 to 3 cars may leave from that road
        - 0 to 2 new cars may arrive on every road
        - Reward depends on whether total traffic improved
        """
        # If someone calls step() before reset(), we create a starting state first.
        if self._state.episode_id is None:
            self.reset()

        previous_total = self._total_cars()
        self._state.current_green = action.road

        cars_waiting = self._get_road_cars(action.road)
        cars_leaving = min(cars_waiting, self._random.randint(1, 3))
        self._set_road_cars(action.road, cars_waiting - cars_leaving)

        # New cars arrive randomly on every road after the light change.
        self._state.north_cars += self._random.randint(0, 2)
        self._state.south_cars += self._random.randint(0, 2)
        self._state.east_cars += self._random.randint(0, 2)
        self._state.west_cars += self._random.randint(0, 2)
        self._state.step_count += 1

        new_total = self._total_cars()
        if new_total < previous_total:
            reward = 1.0
        elif new_total > previous_total:
            reward = 0.0
        else:
            reward = 0.5

        return self._build_observation(reward=reward)

    @property
    def state(self) -> TrafficLightState:
        """Expose the current internal state."""
        return self._state

    def close(self) -> None:
        """
        OpenEnv calls close() after each HTTP request.

        We keep it as a no-op because this demo reuses one shared environment
        instance so state is preserved between /reset and /step requests.
        """
        return None

    def _build_observation(self, reward: float) -> TrafficLightObservation:
        """Convert the internal state into the public observation format."""
        return TrafficLightObservation(
            north_cars=self._state.north_cars,
            south_cars=self._state.south_cars,
            east_cars=self._state.east_cars,
            west_cars=self._state.west_cars,
            current_green=self._state.current_green,
            reward=reward,
            done=False,
        )

    def _total_cars(self) -> int:
        """Useful helper for reward calculation."""
        return (
            self._state.north_cars
            + self._state.south_cars
            + self._state.east_cars
            + self._state.west_cars
        )

    def _get_road_cars(self, road: RoadName) -> int:
        """Read the number of waiting cars for one road."""
        if road == "north":
            return self._state.north_cars
        if road == "south":
            return self._state.south_cars
        if road == "east":
            return self._state.east_cars
        return self._state.west_cars

    def _set_road_cars(self, road: RoadName, value: int) -> None:
        """Update the number of waiting cars for one road."""
        if road == "north":
            self._state.north_cars = value
        elif road == "south":
            self._state.south_cars = value
        elif road == "east":
            self._state.east_cars = value
        else:
            self._state.west_cars = value
