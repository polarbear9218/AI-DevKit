import unittest
from typing import Any

from adk.integration import ACTIONS_APP_ID, CONTEXT, REVIEW_CONTEXT, blockers, trusted_reviewer

SHA = "a" * 40


class IntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pr: dict[str, Any] = {
            "state": "open",
            "draft": False,
            "mergeable": True,
            "mergeable_state": "clean",
            "user": {"login": "program"},
            "head": {"sha": SHA, "ref": "adk/adk-002-pipeline", "repo": {"id": 1}},
            "base": {"ref": "main", "repo": {"id": 1}},
        }
        self.checks = [
            {
                "name": CONTEXT,
                "app": {"id": ACTIONS_APP_ID},
                "head_sha": SHA,
                "status": "completed",
                "conclusion": "success",
            }
        ]
        self.reviews = [
            {
                "id": 1,
                "user": {"login": "reviewer"},
                "state": "APPROVED",
                "commit_id": SHA,
            }
        ]

    def findings(self, reviewer: str = "reviewer", protected: bool = True) -> list[str]:
        return blockers(self.pr, self.checks, self.reviews, SHA, reviewer, "program", protected)

    def test_eligible_at_exact_head(self) -> None:
        self.assertEqual([], self.findings())

    def test_failed_status_and_wrong_source(self) -> None:
        self.checks[0]["conclusion"] = "failure"
        self.assertTrue(self.findings())
        self.checks[0]["conclusion"] = "success"
        self.checks[0]["app"] = {"id": 1}
        self.assertTrue(self.findings())

    def test_stale_review_or_new_blocking_review(self) -> None:
        self.reviews[0]["commit_id"] = "b" * 40
        self.assertTrue(self.findings())
        self.reviews[0]["commit_id"] = SHA
        self.reviews.append(
            {
                "id": 2,
                "user": {"login": "reviewer"},
                "state": "CHANGES_REQUESTED",
                "commit_id": SHA,
            }
        )
        self.assertIn("unresolved changes requested", self.findings())

    def test_missing_review_self_approval_and_protection(self) -> None:
        self.assertTrue(self.findings(reviewer="program"))
        self.assertTrue(self.findings(protected=False))
        self.reviews.clear()
        self.assertTrue(self.findings())

    def test_draft_conflict_wrong_branch_and_changed_head(self) -> None:
        self.pr["draft"] = True
        self.pr["mergeable"] = False
        self.pr["head"]["ref"] = "main"
        self.pr["head"]["sha"] = "b" * 40
        self.assertGreaterEqual(len(self.findings()), 3)

    def test_reviewer_identity_comes_only_from_platform_rules(self) -> None:
        rules = [
            {
                "type": "required_status_checks",
                "parameters": {
                    "required_status_checks": [
                        {"context": REVIEW_CONTEXT, "integration_id": 123},
                    ]
                },
            }
        ]
        observed: list[dict[str, Any]] = [
            {
                "name": REVIEW_CONTEXT,
                "app": {"id": 123, "slug": "example-reviewer"},
                "head_sha": SHA,
                "status": "completed",
                "conclusion": "success",
            }
        ]
        self.assertEqual("example-reviewer[bot]", trusted_reviewer(rules, observed, SHA))
        self.assertEqual("", trusted_reviewer([], observed, SHA))
        self.assertEqual("", trusted_reviewer(rules, observed, "b" * 40))
        observed[0]["app"]["id"] = ACTIONS_APP_ID
        self.assertEqual("", trusted_reviewer(rules, observed, SHA))
