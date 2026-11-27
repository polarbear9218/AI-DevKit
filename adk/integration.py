import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

CONTEXT = "Windows engineering gate"
ACTIONS_APP_ID = 15368
BRANCH = re.compile(r"adk/adk-[0-9]{3}-[a-z0-9]+(?:-[a-z0-9]+)*")
SHA = re.compile(r"[0-9a-f]{40}")


def blockers(
    pr: dict[str, Any],
    checks: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
    target: str,
    reviewer: str,
    actor: str,
    protected: bool,
) -> list[str]:
    failures = []
    head, base = pr["head"], pr["base"]
    if not SHA.fullmatch(target) or head["sha"] != target or base["ref"] != "main":
        failures.append("unexpected PR base or head")
    if not BRANCH.fullmatch(head["ref"]) or head["repo"]["id"] != base["repo"]["id"]:
        failures.append("head is not a repository ADK work branch")
    if pr["state"] != "open" or pr["draft"] or pr["mergeable"] is not True:
        failures.append("PR is not open, ready and conflict-free")
    if pr["mergeable_state"] != "clean" or not protected:
        failures.append("GitHub protection or merge readiness is unconfirmed")
    relevant = [check for check in checks if check["name"] == CONTEXT]
    if len(relevant) != 1 or not all(
        check["app"]["id"] == ACTIONS_APP_ID
        and check["head_sha"] == target
        and check["status"] == "completed"
        and check["conclusion"] == "success"
        for check in relevant
    ):
        failures.append("required check has no unambiguous successful result for head")
    latest = {}
    for review in sorted(reviews, key=lambda item: item["id"]):
        if review["state"] != "COMMENTED":
            latest[review["user"]["login"].casefold()] = review
    approval = latest.get(reviewer.casefold(), {})
    if (
        not reviewer
        or reviewer.casefold() in {actor.casefold(), pr["user"]["login"].casefold()}
        or approval.get("state") != "APPROVED"
        or approval.get("commit_id") != target
    ):
        failures.append("designated independent reviewer has no approval for head")
    if any(review["state"] == "CHANGES_REQUESTED" for review in latest.values()):
        failures.append("unresolved changes requested")
    return failures


class GitHub:
    def __init__(self, repository: str, token: str) -> None:
        self.repository = repository
        self.token = token

    def request(self, route: str, payload: dict[str, str] | None = None) -> Any:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        data = None if payload is None else json.dumps(payload).encode()
        if data is not None:
            headers["Content-Type"] = "application/json"
        if os.name == "nt":
            curl = Path(os.environ["SystemRoot"]) / "System32" / "curl.exe"
            command = [
                str(curl),
                "--disable",
                "--silent",
                "--show-error",
                "--fail",
                "--suppress-connect-headers",
                "--include",
                "--proto",
                "=https",
                "--max-time",
                "30",
                "--header",
                "@-",
            ]
            if data is not None:
                command.extend(["--request", "PUT", "--data-binary", data.decode()])
            results = subprocess.check_output(
                [*command, f"https://api.github.com{route}"],
                input="".join(f"{key}: {value}\n" for key, value in headers.items()).encode(),
            )
            head, separator, body = results.partition(b"\r\n\r\n")
            if not separator or b'rel="next"' in head:
                raise ValueError("incomplete GitHub evidence")
            return json.loads(body)
        request = Request(
            f"https://api.github.com{route}",
            data=data,
            headers=headers,
            method="GET" if data is None else "PUT",
        )
        with urlopen(request, timeout=30) as response:
            if 'rel="next"' in response.headers.get("Link", ""):
                raise ValueError("incomplete paginated evidence")
            return json.load(response)


def rules_hold(rules: list[dict[str, Any]]) -> bool:
    by_type = {rule["type"]: rule.get("parameters", {}) for rule in rules}
    pull = by_type.get("pull_request", {})
    checks = by_type.get("required_status_checks", {})
    return (
        {"deletion", "non_fast_forward"} <= by_type.keys()
        and pull.get("required_approving_review_count", 0) >= 1
        and pull.get("dismiss_stale_reviews_on_push") is True
        and pull.get("require_last_push_approval") is True
        and pull.get("required_review_thread_resolution") is True
        and checks.get("strict_required_status_checks_policy") is True
        and {"context": CONTEXT, "integration_id": ACTIONS_APP_ID}
        in checks.get("required_status_checks", [])
    )


def main() -> int:
    parser = argparse.ArgumentParser(prog="adk integrate")
    parser.add_argument("repository")
    parser.add_argument("number", type=int)
    parser.add_argument("target")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repository):
        parser.error("expected owner/repository")
    if args.number < 1 or not SHA.fullmatch(args.target):
        parser.error("expected positive PR number and full head SHA")
    api = GitHub(args.repository, os.environ.get("ADK_PROGRAM_TOKEN", ""))
    root = f"/repos/{api.repository}"
    route = f"{root}/pulls/{args.number}"
    reviewer = os.environ.get("ADK_REVIEWER_LOGIN", "")
    try:
        repository = api.request(root)
        identity = api.request("/user") if api.token else {}
        pr = api.request(route)
        checks = api.request(f"{root}/commits/{args.target}/check-runs?per_page=100")
        reviews = api.request(f"{route}/reviews?per_page=100")
        rules = api.request(f"{root}/rules/branches/main")
        failures = blockers(
            pr,
            checks["check_runs"],
            reviews,
            args.target,
            reviewer,
            identity.get("login", ""),
            rules_hold(rules),
        )
        permissions = repository.get("permissions", {})
        if permissions.get("admin") is not False or permissions.get("push") is not True:
            failures.append("a non-admin Program identity with push rights is required")
        if not identity.get("login"):
            failures.append("Program identity is unverified")
        if failures:
            print(json.dumps({"head": args.target, "blocked": failures}), file=sys.stderr)
            return 1
        if not args.apply:
            print(json.dumps({"head": args.target, "eligible": True}))
            return 0
        merge = api.request(f"{route}/merge", {"sha": args.target, "merge_method": "merge"})
        updated = api.request(route)
        main_ref = api.request(f"{root}/git/ref/heads/main")
        if (
            merge.get("merged") is not True
            or updated["merged"] is not True
            or updated["merge_commit_sha"] != merge["sha"]
            or main_ref["object"]["sha"] != merge["sha"]
        ):
            raise ValueError("merge result or main SHA could not be verified")
        print(json.dumps({"head": args.target, "merge": merge["sha"]}))
    except (OSError, URLError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f"Integration blocked: {exc}", file=sys.stderr)
        return 1
    return 0
