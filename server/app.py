"""
server/app.py — OpenEnv standard entry point.
The openenv validator expects this file to exist and [project.scripts]
to point here via a `main()` function.
"""
import os
import sys

# Allow imports from the repo root (action, environment, observation, application)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from application import app  # noqa: E402  (import after sys.path fix)


def main() -> None:
    """Entry point called by `uv run server` / the [project.scripts] command."""
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "7860")),
        workers=int(os.getenv("WORKERS", "1")),
    )


if __name__ == "__main__":
    main()
