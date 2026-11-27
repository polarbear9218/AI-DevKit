import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from adk.evaluation import score
from adk.features import cyclic_features, load_catalog, valid_reference
from adk.gate import checkout_commit, scanner_path
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

    def test_verify_commit_rejects_wrong_target(self) -> None:
        subprocess_result = subprocess.run(
            [sys.executable, "-B", "-m", "adk", "verify-commit", "0" * 40],
            cwd=ROOT,
            capture_output=True,
            check=False,
        )
        self.assertEqual(1, subprocess_result.returncode)
        self.assertIn(b"full checked-out HEAD", subprocess_result.stderr)

    def test_commit_checkout_ignores_local_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "source"
            root.mkdir()
            subprocess.run(["git", "init", "--quiet", "--template="], cwd=root, check=True)
            tracked = root / "program.py"
            tracked.write_text("value = 1\n", encoding="utf-8")
            attributes = root / ".gitattributes"
            attributes.write_text("program.py filter=adkprobe\n", encoding="utf-8")
            subprocess.run(["git", "add", "program.py", ".gitattributes"], cwd=root, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Fixture",
                    "-c",
                    "user.email=fixture@example.invalid",
                    "commit",
                    "--quiet",
                    "-m",
                    "fixture",
                ],
                cwd=root,
                check=True,
            )
            target = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=root,
                text=True,
            ).strip()
            subprocess.run(
                ["git", "update-index", "--assume-unchanged", "program.py"],
                cwd=root,
                check=True,
            )
            tracked.write_text("value = 2\n", encoding="utf-8")
            info = root / ".git/info"
            info.mkdir(exist_ok=True)
            (info / "exclude").write_text("ruff.toml\n", encoding="utf-8")
            (root / "ruff.toml").write_text("line-length = 500\n", encoding="utf-8")
            self.assertEqual(
                b"", subprocess.check_output(["git", "status", "--porcelain"], cwd=root)
            )
            snapshot = Path(directory) / "snapshot"
            config = Path(directory) / "gitconfig"
            config.write_text(
                '[filter "adkprobe"]\n    smudge = git hash-object --stdin\n', encoding="utf-8"
            )
            with patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": str(config)}):
                unprotected = Path(directory) / "unprotected"
                subprocess.run(
                    ["git", "clone", "--quiet", "--no-local", str(root), str(unprotected)],
                    check=True,
                )
                for packed_file in (unprotected / ".git/objects/pack").glob("*"):
                    packed_file.chmod(stat.S_IREAD | stat.S_IWRITE)
                self.assertNotEqual(
                    "value = 1\n", (unprotected / "program.py").read_text(encoding="utf-8")
                )
                fake_bin = Path(directory) / "fake-bin"
                fake_bin.mkdir()
                (fake_bin / "git.exe").write_bytes(b"not the selected Git")
                fake_path = str(fake_bin) + os.pathsep + os.environ["PATH"]
                with patch.dict(os.environ, {"PATH": fake_path}):
                    checkout_commit(root, target, snapshot)
            self.assertEqual("value = 1\n", (snapshot / "program.py").read_text(encoding="utf-8"))
            self.assertFalse((snapshot / "ruff.toml").exists())

    def test_scanner_rejects_modified_binary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".tools").mkdir()
            (root / ".tools/gitleaks.exe").write_bytes(b"unexpected executable")
            with self.assertRaisesRegex(ValueError, "Gitleaks"):
                scanner_path(root)
