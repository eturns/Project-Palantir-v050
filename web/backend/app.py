"""Project Palantír — FastAPI web application.

DEV-079-A3-4
Author: Edward Turns (Project Lead)
"""

import json
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

from web.backend.engine_adapter import analyse_army_for_web


MAX_UPLOAD_BYTES = 1024 * 1024

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


@app.post("/api/v1/analyse", tags=["Army Analysis"])
def analyse_army(file: UploadFile = File(...)) -> dict:
    """Analyse an uploaded MESBG List Builder JSON army."""

    if not file.filename or not file.filename.lower().endswith(".json"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a JSON army file.",
        )

    contents = file.file.read(MAX_UPLOAD_BYTES + 1)

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Army file exceeds the 1 MB limit.",
        )

    try:
        data = json.loads(contents.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not valid UTF-8 JSON.",
        ) from None

    if (
        not isinstance(data, dict)
        or not isinstance(data.get("warbands"), list)
        or not isinstance(data.get("metadata"), dict)
    ):
        raise HTTPException(
            status_code=400,
            detail="Not a recognised MESBG List Builder JSON structure.",
        )

    # Use a server-generated temporary path, never the uploaded filename.
    with tempfile.NamedTemporaryFile(
        mode="wb",
        suffix=".json",
        prefix="palantir_upload_",
        delete=False,
    ) as temporary:
        temporary.write(contents)
        temporary_path = Path(temporary.name)

    try:
        try:
            return analyse_army_for_web(temporary_path)
        except (ValueError, KeyError, TypeError, IndexError) as error:
            # Detailed importer errors are intentionally not exposed.
            raise HTTPException(
                status_code=422,
                detail="The army could not be imported or analysed.",
            ) from error
    finally:
        temporary_path.unlink(missing_ok=True)
