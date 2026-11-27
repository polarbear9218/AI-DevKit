import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from adk.evaluation import score
from adk.features import cyclic_features, load_catalog, valid_reference
from adk.policy import check_files, check_markdown, check_python

ROOT = Path(__file__).resolve().parents[1]


class CatalogTests(unittest.TestCase):
    def test_catalog_and_query(self) -> None:
        catalog, errors = load_catalog(ROOT)
        self.assertEqual([], errors)
        result = subprocess.run(
            [sys.executable, "-B", "-m", "adk", "features", "catalog"],
            cwd=ROOT,
            capture_output=True,
            check=True,
        )
        self.assertEqual(["ADK-101"], [record["id"] for record in json.loads(result.stdout)])
        self.assertGreaterEqual(len(catalog), 2)

    def test_dependency_cycle(self) -> None:
        self.assertEqual(["A", "B"], cyclic_features({"A": ["B"], "B": ["A"], "C": []}))

    def test_reference_escape_and_empty_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertFalse(valid_reference(root, root, r"C:\outside"))
            self.assertTrue(load_catalog(root)[1])


class PolicyTests(unittest.TestCase):
    def test_comment_policy_and_architecture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "features.py"
            path.write_text(
                "# SPDX-License-Identifier: MIT\n"
                "from adk import policy\n"
                "value = '# literal'\n"
                "# ordinary note\n"
                "result = 1  # no" + "qa\n",
                encoding="utf-8",
            )
            findings = list(check_python(path, core=True))
            self.assertEqual(3, len(findings))
            self.assertTrue(any("forbidden dependency" in finding for finding in findings))

    def test_missing_document_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "index.md"
            path.write_text("[missing](missing.md)\n[valid](index.md)\n", encoding="utf-8")
            self.assertEqual(1, len(list(check_markdown(root, path))))

    def test_nested_module_cannot_evade_architecture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            relative = Path("adk/nested/module.py")
            path = root / relative
            path.parent.mkdir(parents=True)
            path.write_text("from adk import gate\n", encoding="utf-8")
            self.assertIn(
                "adk/nested/module.py: unregistered ADK module", check_files(root, [relative])
            )


class EvalTests(unittest.TestCase):
    def test_scoring_requires_observations_and_exact_types(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            case = Path(directory) / "case.json"
            result = Path(directory) / "result.json"
            case.write_text(
                '{"checks":{"known":true,"wrong":1,"missing":"value"}}', encoding="utf-8"
            )
            result.write_text(
                '{"session":"fixture","observations":{"known":true,"wrong":true}}', encoding="utf-8"
            )
            self.assertEqual(
                {"known": True, "wrong": False, "missing": False},
                score(case, result),
            )
