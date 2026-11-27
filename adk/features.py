import json
import re
import tomllib
from pathlib import Path, PureWindowsPath
from typing import TypedDict

FEATURE_ID = re.compile(r"[A-Z][A-Z0-9]*-[0-9]{3}")
REQUIRED = {"id", "name", "purpose", "status", "behavior", "requirements"}
LISTS = {
    "aliases",
    "entrypoints",
    "code",
    "dependencies",
    "preconditions",
    "invariants",
    "side_effects",
    "security",
    "verification",
    "requirements",
    "adrs",
    "references",
}
REFERENCES = {"code", "verification", "requirements", "adrs", "references"}


class Feature(TypedDict):
    id: str
    name: str
    status: str
    path: str
    aliases: list[str]
    entrypoints: list[str]


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def valid_reference(root: Path, parent: Path, target: str) -> bool:
    try:
        path = Path(target)
        windows = PureWindowsPath(target)
        if path.is_absolute() or windows.drive or windows.root or "\\" in target:
            return False
        resolved = (parent / path).resolve()
        return resolved.is_relative_to(root) and resolved.is_file()
    except (OSError, ValueError):
        return False


def text_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value)


def read_record(root: Path, path: Path) -> tuple[Feature, list[str]]:
    if not valid_reference(root, root, path.relative_to(root).as_posix()):
        raise ValueError("record is outside repository")
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    if not isinstance(data, dict) or not REQUIRED <= data.keys() or data.keys() - REQUIRED - LISTS:
        raise ValueError("invalid feature fields")
    for field in REQUIRED - {"requirements"}:
        if not isinstance(data[field], str) or not data[field].strip():
            raise ValueError(f"{field} must be nonempty text")
    if data["id"] != path.stem or not FEATURE_ID.fullmatch(data["id"]):
        raise ValueError("invalid feature ID or filename mismatch")
    status = data["status"]
    if status not in {"planned", "implemented", "deprecated"}:
        raise ValueError("invalid lifecycle status")
    for field in LISTS & data.keys():
        if not text_list(data[field]):
            raise ValueError(f"{field} must be a list of nonempty strings")
    if not data["requirements"]:
        raise ValueError("requirements must be nonempty")
    if status == "implemented" and not all(
        data.get(field) for field in ("code", "verification", "entrypoints")
    ):
        raise ValueError("implemented feature requires code, verification and entrypoints")
    for field in sorted(REFERENCES):
        for reference in data.get(field, []):
            if not valid_reference(root, root, reference):
                raise ValueError(f"invalid {field} reference: {reference}")
    return Feature(
        id=data["id"],
        name=data["name"],
        status=status,
        path=path.relative_to(root).as_posix(),
        aliases=data.get("aliases", []),
        entrypoints=data.get("entrypoints", []),
    ), list(data.get("dependencies", []))


def cyclic_features(dependencies: dict[str, list[str]]) -> list[str]:
    pending = {key: set(value) & dependencies.keys() for key, value in dependencies.items()}
    while pending:
        leaves = {key for key, value in pending.items() if not value}
        if not leaves:
            return sorted(pending)
        pending = {key: value - leaves for key, value in pending.items() if key not in leaves}
    return []


def load_catalog(root: Path) -> tuple[list[Feature], list[str]]:
    root = root.resolve()
    features: list[Feature] = []
    dependencies: dict[str, list[str]] = {}
    errors: list[str] = []
    directory = root / "features"
    for path in sorted(directory.glob("*.json")):
        try:
            feature, requires = read_record(root, path)
        except (OSError, ValueError) as exc:
            errors.append(f"{path.name}: {exc}")
            continue
        features.append(feature)
        dependencies[feature["id"]] = requires
    if not features:
        errors.append("features: no valid feature records")
    for feature_id, requires in dependencies.items():
        for missing in sorted(set(requires) - dependencies.keys()):
            errors.append(f"{feature_id}: unknown dependency {missing}")
    if cycle := cyclic_features(dependencies):
        errors.append(f"feature dependency cycle or dependent on cycle: {', '.join(cycle)}")
    return features, errors


def validate_config(root: Path) -> list[str]:
    with (root / "pyproject.toml").open("rb") as config:
        tools = tomllib.load(config)["tool"]
    ruff = tools["ruff"]
    lint = ruff["lint"]
    mypy = tools["mypy"]
    errors: list[str] = []
    if not {"E4", "E7", "E9", "F", "I", "UP", "B", "RUF", "PGH004"} <= set(lint.get("select", [])):
        errors.append("Ruff required rules missing")
    if set(ruff) - {"target-version", "line-length", "lint"} or set(lint) - {"select"}:
        errors.append("unexpected Ruff configuration; suppression requires governance")
    if mypy != {"strict": True, "python_version": "3.12"}:
        errors.append("unexpected mypy configuration; suppression requires governance")
    return errors
