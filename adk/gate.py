import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def checkout_commit(root: Path, target: str, snapshot: Path) -> None:
    if not re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", target):
        raise ValueError("target must be a full commit SHA")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    if head != target:
        raise ValueError(f"target must be the full checked-out HEAD ({head})")
    subprocess.run(
        [
            "git",
            "clone",
            "--quiet",
            "--no-local",
            "--no-checkout",
            "--template=",
            str(root),
            str(snapshot),
        ],
        check=True,
        cwd=root,
    )
    subprocess.run(["git", "checkout", "--quiet", "--detach", target], check=True, cwd=snapshot)


def verify_commit(root: Path, target: str) -> int:
    with tempfile.TemporaryDirectory() as directory:
        snapshot = Path(directory) / "target"
        checkout_commit(root, target, snapshot)
        executable = "gitleaks.exe" if os.name == "nt" else "gitleaks"
        (snapshot / ".tools").mkdir(exist_ok=True)
        shutil.copy2(root / ".tools" / executable, snapshot / ".tools" / executable)
        environment = {
            key: value
            for key, value in os.environ.items()
            if not key.upper().startswith(("PYTHON", "GITLEAKS", "MYPY", "RUFF"))
        }
        return subprocess.run(
            [sys.executable, "-E", "-s", "-B", "-m", "adk", "verify"],
            cwd=snapshot,
            env=environment,
            check=False,
        ).returncode


def verify(root: Path) -> int:
    executable = "gitleaks.exe" if os.name == "nt" else "gitleaks"
    gitleaks = root / ".tools" / executable
    commands = [
        [
            sys.executable,
            "-m",
            "ruff",
            "format",
            "--check",
            "--no-cache",
            "--config",
            "pyproject.toml",
            "adk",
            "tests",
        ],
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--no-cache",
            "--config",
            "pyproject.toml",
            "adk",
            "tests",
        ],
        [
            sys.executable,
            "-m",
            "mypy",
            "--no-incremental",
            "--config-file",
            "pyproject.toml",
            "adk",
            "tests",
        ],
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
    ]
    failed = False
    with tempfile.TemporaryDirectory() as directory:
        scan_root = Path(directory)
        paths = subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root
        )
        for name in set(paths.split(b"\0")) - {b""}:
            relative = Path(name.decode("utf-8"))
            destination = scan_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((root / relative).read_bytes())
        commands.append([str(gitleaks), "dir", "--redact=100", "--no-banner", str(scan_root)])
        for command in commands:
            label = (
                command[2]
                if command[0] == sys.executable and command[1] == "-m"
                else ("unittest" if command[0] == sys.executable else "gitleaks")
            )
            print(f"Running {label}", flush=True)
            try:
                failed |= subprocess.run(command, cwd=root, check=False).returncode != 0
            except OSError as exc:
                print(f"{label}: {exc}", file=sys.stderr)
                failed = True
    return int(failed)
