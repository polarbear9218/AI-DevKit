import json
from pathlib import Path


def score(case_path: Path, result_path: Path) -> dict[str, bool]:
    case = json.loads(case_path.read_text(encoding="utf-8-sig"))
    result = json.loads(result_path.read_text(encoding="utf-8-sig"))
    checks = case["checks"]
    observations = result["observations"]
    if not isinstance(checks, dict) or not checks or not isinstance(observations, dict):
        raise ValueError("expected nonempty checks and an observations object")
    if not isinstance(result.get("session"), str) or not result["session"].strip():
        raise ValueError("an actual Agent session identifier is required")
    if any(type(expected) not in {bool, str, int} for expected in checks.values()):
        raise ValueError("checks must be boolean, text or integer")
    return {
        key: type(observations.get(key)) is type(expected) and observations[key] == expected
        for key, expected in checks.items()
    }
