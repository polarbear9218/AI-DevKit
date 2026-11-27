import os
import subprocess
import sys
import tempfile
from pathlib import Path


def verify(root: Path) -> int:
    executable = "gitleaks.exe" if os.name == "nt" else "gitleaks"
    gitleaks = root / ".tools" / executable
    commands = [
        [sys.executable, "-m", "ruff", "format", "--check", "--no-cache", "adk", "tests"],
        [sys.executable, "-m", "ruff", "check", "--no-cache", "adk", "tests"],
        [sys.executable, "-m", "mypy", "--no-incremental", "adk", "tests"],
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
