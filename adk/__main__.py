import argparse
import json
import subprocess
import sys
from pathlib import Path

from adk.features import load_catalog, validate_config
from adk.policy import check_files


def repository_files(root: Path) -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
    )
    return sorted({Path(name.decode("utf-8")) for name in output.split(b"\0") if name})


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m adk")
    parser.add_argument("command", choices=("features", "check", "verify"))
    parser.add_argument("query", nargs="?", default="")
    args = parser.parse_args()
    root = Path.cwd()
    try:
        catalog, errors = load_catalog(root)
        if args.command == "features":
            if not errors:
                matches = [
                    feature
                    for feature in catalog
                    if args.query.casefold()
                    in " ".join((feature["id"], feature["name"], *feature["aliases"])).casefold()
                ]
                print(json.dumps(matches, ensure_ascii=True, indent=2))
                return int(bool(args.query and not matches))
        else:
            errors.extend(validate_config(root))
            errors.extend(check_files(root, repository_files(root)))
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        errors = [str(exc)]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if args.command == "verify":
        from adk.gate import verify

        return verify(root)
    print("Repository policy checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
