import hashlib
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

GIT_WINDOWS_SHA256 = "bf50371f964f7be61a76ebad7dce8b6197afd47b5b588fc62780823aa097ff63"
PORTABLE_GIT_SHA256 = "9bf8ee81d79f38a11eaf7799499a634c46a718e009a4a9b2b20b115804643302"
GITLEAKS_WINDOWS_SHA256 = "9d08e3f5cfb35a98f230b97bcda24f8d3fc66363c91868ffc98dac0afebdcb72"


def verify_executable(path: Path, expected: str, label: str) -> Path:
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != expected:
        raise ValueError(f"{label} binary checksum mismatch")
    return path


def git_command() -> str:
    if os.name != "nt":
        return "git"
    if override := os.environ.get("ADK_GIT_EXECUTABLE"):
        portable = Path(override)
        if not portable.is_absolute():
            raise ValueError("ADK_GIT_EXECUTABLE must be an absolute path")
        return str(verify_executable(portable, PORTABLE_GIT_SHA256, "PortableGit"))
    install_root = Path(os.environ.get("ProgramFiles", "C:/Program Files"))
    if not install_root.is_absolute():
        raise ValueError("Git for Windows must be installed in an absolute Program Files path")
    executable = install_root / "Git" / "mingw64" / "bin" / "git.exe"
    return str(verify_executable(executable, GIT_WINDOWS_SHA256, "Git"))


def isolated_environment() -> dict[str, str]:
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.upper().startswith(("GIT_", "PYTHON", "GITLEAKS", "MYPY", "RUFF"))
    }
    environment.update(
        GIT_CONFIG_GLOBAL=os.devnull,
        GIT_CONFIG_NOSYSTEM="1",
        GIT_ATTR_NOSYSTEM="1",
    )
    return environment


def scanner_path(root: Path) -> Path:
    if os.name != "nt":
        raise ValueError("the verified Gitleaks binary is pinned for Windows x64")
    return verify_executable(root / ".tools" / "gitleaks.exe", GITLEAKS_WINDOWS_SHA256, "Gitleaks")


def checkout_commit(root: Path, target: str, snapshot: Path) -> None:
    environment = isolated_environment()
    git = git_command()
    if not re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", target):
        raise ValueError("target must be a full commit SHA")
    head = subprocess.check_output(
        [git, "rev-parse", "HEAD"], cwd=root, text=True, env=environment
    ).strip()
    if head != target:
        raise ValueError(f"target must be the full checked-out HEAD ({head})")
    subprocess.run(
        [
            git,
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
        env=environment,
    )
    for packed_file in (snapshot / ".git" / "objects" / "pack").glob("*"):
        packed_file.chmod(stat.S_IREAD | stat.S_IWRITE)
    subprocess.run(
        [git, "checkout", "--quiet", "--detach", target],
        check=True,
        cwd=snapshot,
        env=environment,
    )


def verify_commit(root: Path, target: str) -> int:
    with tempfile.TemporaryDirectory() as directory:
        snapshot = Path(directory) / "target"
        checkout_commit(root, target, snapshot)
        executable = scanner_path(root)
        (snapshot / ".tools").mkdir(exist_ok=True)
        shutil.copy2(executable, snapshot / ".tools" / executable.name)
        return subprocess.run(
            [sys.executable, "-E", "-s", "-B", "-m", "adk", "verify"],
            cwd=snapshot,
            env=isolated_environment(),
            check=False,
        ).returncode


def verify(root: Path) -> int:
    gitleaks = scanner_path(root)
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
            [git_command(), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=root,
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
