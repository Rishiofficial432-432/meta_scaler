import requests

BASE_URL = "http://127.0.0.1:8000/openenv"


def choose_road_with_max_cars(observation: dict) -> str:
    """Pick the road that currently has the most cars waiting."""
    road_counts = {
        "north": observation["north_cars"],
        "south": observation["south_cars"],
        "east": observation["east_cars"],
        "west": observation["west_cars"],
    }
    return max(road_counts, key=road_counts.get)


def print_observation(title: str, observation: dict, reward: float | None = None) -> None:
    """Print the current state in a friendly format."""
    print(f"\n{title}")
    print(f"  North cars: {observation['north_cars']}")
    print(f"  South cars: {observation['south_cars']}")
    print(f"  East cars:  {observation['east_cars']}")
    print(f"  West cars:  {observation['west_cars']}")
    print(f"  Green road: {observation['current_green']}")
    if reward is not None:
        print(f"  Reward:     {reward}")


def main() -> None:
    """Run 10 inference steps against the local FastAPI server."""
    reset_response = requests.post(f"{BASE_URL}/reset", json={}, timeout=10)
    reset_response.raise_for_status()

    reset_data = reset_response.json()
    observation = reset_data["observation"]
    print_observation("Initial observation after reset", observation, reset_data.get("reward"))

    for step_number in range(1, 11):
        road = choose_road_with_max_cars(observation)
        step_payload = {"action": {"road": road}}

        step_response = requests.post(
            f"{BASE_URL}/step",
            json=step_payload,
            timeout=10,
        )
        step_response.raise_for_status()

        step_data = step_response.json()
        observation = step_data["observation"]

        print(f"\nStep {step_number}")
        print(f"Chosen action: {road}")
        print_observation("Observation", observation, step_data.get("reward"))

        if step_data.get("done"):
            print("\nEpisode finished early.")
            break


if __name__ == "__main__":
    main()
