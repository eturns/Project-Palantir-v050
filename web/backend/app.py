"""Project Palantír — DEV-079 web backend.

Author: Edward Turns (Project Lead)
"""

from fastapi import FastAPI

app = FastAPI(
    title="Project Palantír API",
    description="MESBG army analysis powered by the Palantír Python engine.",
    version="0.1.0",
)


@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "application": "Project Palantír",
        "api_version": "0.1.0",
    }
