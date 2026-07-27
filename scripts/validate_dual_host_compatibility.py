#!/usr/bin/env python3
"""Validate Codex/Hermes repository compatibility without live mutations."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILLS_ROOT = REPO_ROOT / "skills"
DEFAULT_PLUGINS_ROOT = REPO_ROOT / "plugins"


_YAML_BLOCK_MARKER = re.compile(r"[|>][+-]?")
_YAML_INTEGER = re.compile(r"[-+]?(?:0|[1-9][0-9]*)")
_YAML_FLOAT = re.compile(
    r"[-+]?(?:(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[eE][-+]?[0-9]+)?|"
    r"[0-9]+[eE][-+]?[0-9]+)"
)


class _QuotedYamlString(str):
    pass


def _parse_yaml_scalar(value: str) -> object:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return _QuotedYamlString(value[1:-1])
    lowered = value.lower()
    if lowered in {"null", "~"}:
        return None
    if lowered in {"true", "false"}:
        return lowered == "true"
    if _YAML_INTEGER.fullmatch(value):
        return int(value)
    if _YAML_FLOAT.fullmatch(value):
        return float(value)
    if (
        len(value) >= 2
        and (value[0], value[-1]) in {("[", "]"), ("{", "}")}
    ):
        return object()
    return value


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_non_empty_yaml_scalar(value: object) -> bool:
    if not _is_non_empty_string(value):
        return False
    if isinstance(value, _QuotedYamlString):
        return True
    return _YAML_BLOCK_MARKER.fullmatch(value.strip()) is None


def parse_skill_frontmatter(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = next(
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == "---"
        )
    except StopIteration:
        return {}
    parsed = {}
    for raw_line in lines[1:end]:
        if not raw_line or raw_line[:1].isspace() or ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        parsed[key.strip()] = _parse_yaml_scalar(value)
    return parsed


def parse_top_level_yaml_scalars(path: Path) -> dict[str, object]:
    parsed = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line or line[:1].isspace() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        parsed[key.strip()] = _parse_yaml_scalar(value)
    return parsed


def _register_function(path: Path) -> ast.FunctionDef | None:
    try:
        module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError):
        return None
    return next(
        (
            node
            for node in module.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "register"
            and not node.args.posonlyargs
            and len(node.args.args) == 1
            and node.args.args[0].arg == "ctx"
            and node.args.vararg is None
            and not node.args.kwonlyargs
            and node.args.kwarg is None
            and not node.args.defaults
        ),
        None,
    )


def _registered_skill_names(function: ast.FunctionDef) -> set[str]:
    names = set()

    class RegisterBodyVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            return None

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            return None

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            return None

        def visit_Lambda(self, node: ast.Lambda) -> None:
            return None

        def visit_Call(self, node: ast.Call) -> None:
            if (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "ctx"
                and node.func.attr == "register_skill"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and type(node.args[0].value) is str
            ):
                names.add(node.args[0].value)
            self.generic_visit(node)

    visitor = RegisterBodyVisitor()
    for statement in function.body:
        visitor.visit(statement)
    return names


def validate_skill(skill_dir: Path) -> list[str]:
    entrypoint = skill_dir / "SKILL.md"
    if not entrypoint.is_file():
        return [f"{skill_dir.name}/SKILL.md is required"]
    fields = parse_skill_frontmatter(entrypoint)
    errors = []
    skill_name = fields.get("name")
    if (
        not _is_non_empty_yaml_scalar(skill_name)
        or skill_name != skill_dir.name
    ):
        errors.append(f"{skill_dir.name}: frontmatter name must equal directory name")
    if not _is_non_empty_yaml_scalar(fields.get("description")):
        errors.append(f"{skill_dir.name}: frontmatter description must be non-empty")
    if any(entry.name == "description.md" for entry in skill_dir.iterdir()):
        errors.append(
            f"{skill_dir.name}: SKILL.md must not depend on description.md for discovery"
        )
    return errors


def validate_plugin(plugin_dir: Path) -> list[str]:
    name = plugin_dir.name
    codex_path = plugin_dir / ".codex-plugin" / "plugin.json"
    hermes_path = plugin_dir / "plugin.yaml"
    entrypoint = plugin_dir / "__init__.py"
    errors = []
    for path, label in (
        (codex_path, ".codex-plugin/plugin.json"),
        (hermes_path, "plugin.yaml"),
        (entrypoint, "__init__.py"),
    ):
        if not path.is_file():
            errors.append(f"{name}: {label} is required")
    if errors:
        return errors
    try:
        codex = json.loads(codex_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return [f"{name}: Codex manifest must be valid JSON"]
    if not isinstance(codex, dict):
        return [f"{name}: Codex manifest must be a JSON object"]
    hermes = parse_top_level_yaml_scalars(hermes_path)
    if codex.get("name") != name or hermes.get("name") != name:
        errors.append(f"{name}: manifest names must equal directory name")
    codex_version = codex.get("version")
    hermes_version = hermes.get("version")
    codex_version_valid = _is_non_empty_string(codex_version)
    hermes_version_valid = _is_non_empty_yaml_scalar(hermes_version)
    if not codex_version_valid:
        errors.append(f"{name}: Codex version must be a non-empty string")
    if not hermes_version_valid:
        errors.append(f"{name}: Hermes version must be a non-empty string")
    if (
        codex_version_valid
        and hermes_version_valid
        and codex_version != hermes_version
    ):
        errors.append(f"{name}: Codex and Hermes versions must match")
    codex_description = codex.get("description")
    if not isinstance(codex_description, str) or not codex_description.strip():
        errors.append(f"{name}: Codex description must be non-empty")
    if not _is_non_empty_yaml_scalar(hermes.get("description")):
        errors.append(f"{name}: Hermes description must be non-empty")
    manifest_version = hermes.get("manifest_version")
    if type(manifest_version) is not int or manifest_version != 1:
        errors.append(f"{name}: Hermes manifest_version must be integer 1")
    if not _is_non_empty_yaml_scalar(hermes.get("kind")):
        errors.append(f"{name}: Hermes kind must be non-empty")
    register = _register_function(entrypoint)
    if register is None:
        errors.append(f"{name}: __init__.py must define register(ctx)")
        return errors
    skills_dir = plugin_dir / "skills"
    bundled = list(skills_dir.rglob("SKILL.md")) if skills_dir.is_dir() else []
    bundled_names = set()
    for bundled_dir in sorted({path.parent for path in bundled}):
        errors.extend(validate_skill(bundled_dir))
        bundled_name = parse_skill_frontmatter(bundled_dir / "SKILL.md").get("name")
        if (
            _is_non_empty_yaml_scalar(bundled_name)
            and bundled_name == bundled_dir.name
        ):
            bundled_names.add(bundled_name)
    registered_names = _registered_skill_names(register)
    for bundled_name in sorted(bundled_names - registered_names):
        errors.append(
            f"{name}: bundled skill {bundled_name!r} requires matching "
            "ctx.register_skill(...)"
        )
    return errors


def validate_repository(skills_root: Path, plugins_root: Path) -> list[str]:
    errors = []
    if not skills_root.is_dir():
        errors.append(f"skills root is not a directory: {skills_root}")
    if skills_root.is_dir():
        for path in sorted(item for item in skills_root.iterdir() if item.is_dir()):
            errors.extend(validate_skill(path))
    if not plugins_root.is_dir():
        errors.append(f"plugins root is not a directory: {plugins_root}")
    if plugins_root.is_dir():
        for path in sorted(item for item in plugins_root.iterdir() if item.is_dir()):
            errors.extend(validate_plugin(path))
    return errors


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    target = result.add_mutually_exclusive_group(required=True)
    target.add_argument("--all", action="store_true")
    target.add_argument("--skill", type=Path)
    target.add_argument("--plugin", type=Path)
    result.add_argument("--skills-root", type=Path, default=DEFAULT_SKILLS_ROOT)
    result.add_argument("--plugins-root", type=Path, default=DEFAULT_PLUGINS_ROOT)
    result.add_argument("--json", action="store_true")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.all:
        errors = validate_repository(args.skills_root, args.plugins_root)
    elif args.skill is not None:
        errors = validate_skill(args.skill)
    else:
        errors = validate_plugin(args.plugin)
    if args.json:
        print(json.dumps({"ok": not errors, "errors": errors}, indent=2))
    elif errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
    else:
        print("OK: dual-host repository compatibility")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
