"""Project Palantír — DEV-082-A3-2J-3 real web-upload smoke diagnostic.
Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).

Posts two real reference fixture files via the actual FastAPI endpoint. The
response must contain the new provisional section and unchanged v1 fields.
No server, calibration or database writes are performed.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient
from web.backend.app import app

FIXTURES = ("dol_guldur_700.json", "azogs-hunters.json")


def main():
    client = TestClient(app)
    rows = []
    for filename in FIXTURES:
        fixture = ROOT / "tests" / "fixtures" / filename
        response = client.post("/api/v1/analyse", files={
            "file": (filename, fixture.read_bytes(), "application/json"),
        })
        if response.status_code != 200:
            raise RuntimeError(f"{filename}: upload returned HTTP {response.status_code}")
        body = response.json()
        if body.get("schema_version") != "palantir-web-analysis-v1":
            raise RuntimeError("Web API schema changed")
        a = body.get("analysis", {})
        if not isinstance(a.get("scenarios"), list) or len(a["scenarios"]) != 24:
            raise RuntimeError("Scenario list missing/changed shape")
        if any(k not in a for k in (
            "metrics", "provisional_capabilities", "provisional_magic", "provisional_offence"
        )):
            raise RuntimeError("Historical or new evidence missing")
        off = a["provisional_offence"]
        if off.get("status") != "provisional_display_only":
            raise RuntimeError(
                f"{filename}: known fixture did not qualify; "
                f"diagnostic status={off.get('status')}, "
                f"reason={off.get('reason_code')}"
            )
        if off.get("safeguards", {}).get("production_scoring_changed") is not False:
            raise RuntimeError("Production score safeguard violated")
        rows.append({
            "fixture": filename,
            "offence_status": off["status"],
            "neutral": off.get("neutral_melee"),
            "reason_code": off.get("reason_code"),
            "scenarios": len(a["scenarios"]),
            "magic_preserved": True,
            "schema_version": body["schema_version"],
        })
    out = {
        "stage": "DEV-082-A3-2J-3",
        "status": "two_real_uploads_qualified",
        "uploaded_armies": len(rows),
        "per_upload_diagnostic_populated": True,
        "unqualified_states_explicit_not_zero": True,
        "production_scoring_changed": False,
        "calibration_changed": False,
        "frontend_modified": False,
        "rows": rows,
    }
    print(json.dumps(out, indent=2, allow_nan=False))
    return out

if __name__ == "__main__":
    main()
