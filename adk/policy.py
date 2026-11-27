import ast
import re
import tokenize
from collections.abc import Iterable
from pathlib import Path

from adk.features import valid_reference

SPDX = re.compile(r"# SPDX-(?:License-Identifier|FileCopyrightText): \S.*")
ENCODING = re.compile(r"# [*-]*\s*coding[:=]\s*utf-8\s*(?:-\*-)?", re.IGNORECASE)
LINK = re.compile(r"!?\[[^\]\n]+\]\(([^\s()]+)\)")
SUPPRESSION = re.compile(r"\b(?:noqa|nosec|type:\s*ignore|ruff:|mypy:|pylint:|fmt:|pyright:)", re.I)

CORE_IMPORTS = {
    "features": set(),
    "policy": {"features"},
    "gate": set(),
    "evaluation": set(),
    "integration": set(),
}
TEST_BYPASS = {"skip", "skipIf", "skipUnless", "skipTest", "expectedFailure"}


def allowed_comment(text: str, line: int) -> bool:
    return (
        (line == 1 and text == "#!/usr/bin/env python3")
        or (line <= 2 and bool(ENCODING.fullmatch(text)))
        or (line <= 5 and bool(SPDX.fullmatch(text)))
    ) and not SUPPRESSION.search(text)


def imported_modules(tree: ast.AST) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(
                alias.name.split(".")[1] for alias in node.names if alias.name.startswith("adk.")
            )
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.startswith("adk."):
                modules.add(module.split(".")[1])
            elif module == "adk" or (node.level and not module):
                modules.update(alias.name for alias in node.names)
            elif node.level:
                modules.add(module.split(".")[0])
    return modules


def check_python(path: Path, *, core: bool = False, tests: bool = False) -> Iterable[str]:
    with tokenize.open(path) as stream:
        source = stream.read()
    with path.open("rb") as stream:
        for token in tokenize.tokenize(stream.readline):
            if token.type == tokenize.COMMENT and not allowed_comment(token.string, token.start[0]):
                yield f"{token.start[0]}: unauthorized comment or suppression"
    tree = ast.parse(source, filename=str(path))
    if core:
        for module in sorted(imported_modules(tree) - CORE_IMPORTS.get(path.stem, set())):
            yield f"forbidden dependency adk.{path.stem} -> adk.{module}"
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if ast.get_docstring(node, clean=False) is not None:
                public_name = (
                    node.name
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                    else ""
                )
                doc = ast.get_docstring(node) or ""
                if (
                    not public_name
                    or public_name.startswith("_")
                    or not doc.startswith("Contract: ")
                ):
                    yield f"{getattr(node, 'lineno', 1)}: unauthorized docstring"
        if tests and isinstance(node, (ast.Name, ast.Attribute)):
            name = node.id if isinstance(node, ast.Name) else node.attr
            if name in TEST_BYPASS:
                yield f"{node.lineno}: unauthorized test skip or expected failure"


def check_markdown(root: Path, path: Path) -> Iterable[str]:
    inside_fence = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            inside_fence = not inside_fence
            continue
        if inside_fence:
            continue
        for match in LINK.finditer(line):
            reference = match[1]
            if reference.startswith(("https://", "http://", "mailto:", "#")):
                continue
            target = reference.split("#", 1)[0]
            if not valid_reference(root, path.parent, target):
                yield f"{number}: missing or unsafe documentation reference: {reference}"


def check_files(root: Path, files: Iterable[Path]) -> list[str]:
    errors: list[str] = []
    for relative in files:
        path = root / relative
        if not valid_reference(root, root, relative.as_posix()):
            errors.append(f"{relative}: missing or unsafe file")
            continue
        if (
            relative.parts[0] == "adk"
            and path.suffix == ".py"
            and (
                relative.parent != Path("adk")
                or relative.stem not in {*CORE_IMPORTS, "__main__", "__init__"}
            )
        ):
            errors.append(f"{relative.as_posix()}: unregistered ADK module")
        try:
            if path.suffix == ".py":
                findings = check_python(
                    path,
                    core=relative.parent == Path("adk") and path.stem != "__main__",
                    tests=relative.parts[0] == "tests",
                )
            elif path.suffix == ".md":
                findings = check_markdown(root, path)
            else:
                continue
            errors.extend(f"{relative.as_posix()}: {finding}" for finding in findings)
        except (OSError, UnicodeError, SyntaxError, tokenize.TokenError) as exc:
            errors.append(f"{relative.as_posix()}: {exc}")
    return errors
