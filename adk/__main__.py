import argparse
import json
import subprocess
import sys
from pathlib import Path

from adk.evaluation import score
from adk.features import load_catalog, validate_config
from adk.gate import git_command, verify, verify_commit
from adk.policy import check_files


def repository_files(root: Path) -> list[Path]:
    output = subprocess.check_output(
        [git_command(), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
    )
    return sorted({Path(name.decode("utf-8")) for name in output.split(b"\0") if name})


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m adk")
    parser.add_argument("command", choices=("features", "check", "verify", "verify-commit", "eval"))
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument("observations", nargs="?")
    args = parser.parse_args()
    if args.command == "eval":
        if not args.query or not args.observations:
            parser.error("eval requires CASE and OBSERVATIONS")
        try:
            results = score(Path(args.query), Path(args.observations))
        except (OSError, ValueError, TypeError, KeyError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(json.dumps(results, sort_keys=True))
        return int(not all(results.values()))
    if args.command == "verify-commit":
        if not args.query or args.observations:
            parser.error("verify-commit requires a full commit SHA")
        try:
            result = verify_commit(Path.cwd(), args.query)
        except (ValueError, OSError, subprocess.SubprocessError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"Verification target {args.query}: exit {result}")
        return result
    if args.observations or (args.query and args.command != "features"):
        parser.error("only features accepts a query")
    return run_checks(Path.cwd(), args.command, args.query)


def run_checks(root: Path, command: str, query: str = "") -> int:
    try:
        catalog, errors = load_catalog(root)
        if command == "features":
            if not errors:
                matches = [
                    feature
                    for feature in catalog
                    if query.casefold()
                    in " ".join((feature["id"], feature["name"], *feature["aliases"])).casefold()
                ]
                print(json.dumps(matches, ensure_ascii=True, indent=2))
                return int(bool(query and not matches))
        else:
            errors.extend(validate_config(root))
            errors.extend(check_files(root, repository_files(root)))
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        errors = [str(exc)]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if command == "verify":
        try:
            return verify(root)
        except (ValueError, OSError, subprocess.SubprocessError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
    print("Repository policy checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
