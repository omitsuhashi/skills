---
kind: synthesis
created: 2026-07-17
updated: 2026-07-17
---

# Codex / Hermes Dual-host Authoring Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** skill / plugin が Codex と Hermes Agent の repository compatibility を満たすことを、薄い guidance、共通 validator、既存成果物の導入契約、CI で保証する。

**Architecture:** 標準 `SKILL.md` は両 host で共有し、plugin だけ host 別の薄い manifest / registration adapter を持つ。Python 3.9+ standard library の validator は静的互換性だけを検証し、plugin 固有 test と hermetic smoke が runtime registration を検証する。distribution / discovery と live load は別の検証段階とし、通常 CI は user の Hermes profile を変更しない。

**Tech Stack:** Markdown、Python 3.9+ standard library、`unittest`、JSON、YAML top-level scalar parsing、Python `ast`、GitHub Actions、Hermes CLI。

## Global Constraints

- skill / plugin は Codex と Hermes Agent の双方を必須 target とする。
- Hermes skill は `SKILL.md` と非空の `name` / `description` を持つ。`description.md` は作らない。
- `agents/openai.yaml` は Codex UI metadata であり Hermes discovery の代替にしない。
- plugin は `.codex-plugin/plugin.json`、`plugin.yaml`、`__init__.py`、`register(ctx)` を持つ。
- standalone companion skill を plugin 内へ複製しない。
- repository compatibility、distribution / discovery、live load を同一視しない。
- validator は standard library のみを使い、live Hermes state を変更しない。
- skill directory 内へ README や install guide を追加しない。
- Goal JSON artifacts は Git 管理対象のまま維持する。

---

## File Map

Create:

- `skills/AGENTS.md`
- `plugins/AGENTS.md`
- `scripts/test_dual_host_authoring_guidance.py`
- `scripts/validate_dual_host_compatibility.py`
- `scripts/test_validate_dual_host_compatibility.py`

Modify:

- `AGENTS.md`
- `plugins/task-management/README.md`
- `plugins/task-management/tests/test_hermes_plugin_manifest.py`
- `skills/decide-in-order/tests/test_skill_contract.py`
- `.github/workflows/skill-architecture.yml`
- `knowledge/wiki/syntheses/hermes-dual-host-authoring-contract-design.md`
- `knowledge/index.md`
- `knowledge/log.md`

## Task 1: Thin dual-host authoring guidance

**Files:**

- Create: `scripts/test_dual_host_authoring_guidance.py`
- Modify: `AGENTS.md`
- Create: `skills/AGENTS.md`
- Create: `plugins/AGENTS.md`

**Interfaces:**

- Consumes: approved three-stage design.
- Produces: root router and directory-local authoring contracts.

- [ ] **Step 1: Write the failing guidance contract test**

Create `scripts/test_dual_host_authoring_guidance.py`:

~~~python
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "AGENTS.md"
SKILLS = REPO_ROOT / "skills" / "AGENTS.md"
PLUGINS = REPO_ROOT / "plugins" / "AGENTS.md"


class DualHostAuthoringGuidanceTests(unittest.TestCase):
    def test_root_routes_to_directory_contracts(self):
        text = ROOT.read_text(encoding="utf-8")
        for value in ("Codex and Hermes Agent", "skills/AGENTS.md", "plugins/AGENTS.md"):
            self.assertIn(value, text)

    def test_skill_contract_names_entrypoint_and_discovery_boundary(self):
        text = SKILLS.read_text(encoding="utf-8")
        for value in (
            "SKILL.md", "name", "description", "description.md",
            "agents/openai.yaml", "skills.external_dirs", "hermes skills list",
        ):
            self.assertIn(value, text)
        self.assertIn("must not create `description.md`", text)

    def test_plugin_contract_names_manifests_and_registration(self):
        text = PLUGINS.read_text(encoding="utf-8")
        for value in (
            ".codex-plugin/plugin.json", "plugin.yaml", "__init__.py",
            "register(ctx)", "ctx.register_skill", "standalone companion skill",
            "hermes plugins list",
        ):
            self.assertIn(value, text)


if __name__ == "__main__":
    unittest.main()
~~~

- [ ] **Step 2: Run RED**

Run:

~~~bash
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/test_dual_host_authoring_guidance.py
~~~

Expected: FAIL because the directory guidance files are missing.

- [ ] **Step 3: Add the root router**

Append:

~~~markdown
## Dual-host authoring

- Skills and plugins created or changed in this repository must target both Codex and Hermes Agent.
- For skill requirements, follow `skills/AGENTS.md`.
- For plugin requirements, follow `plugins/AGENTS.md`.
~~~

- [ ] **Step 4: Create `skills/AGENTS.md`**

~~~markdown
# Skill authoring contract

- Skills in this directory must be readable by both Codex and Hermes Agent.
- Use `<skill-name>/SKILL.md` as the shared entrypoint. Its frontmatter must contain a non-empty `name` and `description`, and the directory name must equal `name`.
- Hermes discovery does not require a separate description file; must not create `description.md` as a discovery requirement.
- `agents/openai.yaml` is Codex UI metadata and does not make a skill discoverable in Hermes.
- Keep host-specific tool assumptions conditional and document a capability check, alternative, or platform boundary.
- Document one Hermes discovery route: GitHub install or tap, `~/.hermes/skills/`, or `skills.external_dirs`.
- Repository compatibility is not live availability. For approved live verification, confirm the skill in `hermes skills list`.
- Run the repository dual-host validator and skill-creator validator before handoff.
~~~

- [ ] **Step 5: Create `plugins/AGENTS.md`**

~~~markdown
# Plugin authoring contract

- Plugins in this directory must be loadable by both Codex and Hermes Agent.
- Keep `.codex-plugin/plugin.json` and `plugin.yaml`; keep their `name`, `version`, and non-empty descriptions coherent.
- A Hermes plugin must have importable `__init__.py` with `register(ctx)`. Register bundled skills with `ctx.register_skill(...)`.
- Keep manifest tool declarations aligned with runtime registration through plugin-specific tests.
- Treat a standalone companion skill as a separate install prerequisite. Do not copy its source into the plugin. Document behavior when unavailable.
- Repository compatibility is not live availability. For approved live verification, confirm enablement and version with `hermes plugins list`, then run the plugin smoke.
- Do not mutate a live Hermes profile, marketplace, credential, or install state during ordinary validation.
- Run the repository dual-host validator and plugin-creator validator before handoff.
~~~

- [ ] **Step 6: Run GREEN and commit**

~~~bash
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/test_dual_host_authoring_guidance.py
git add AGENTS.md skills/AGENTS.md plugins/AGENTS.md scripts/test_dual_host_authoring_guidance.py
git commit -m "Define dual-host authoring guidance"
~~~

Expected: 3 tests OK and one scoped commit.

## Task 2: Standard-library compatibility validator

**Files:**

- Create: `scripts/test_validate_dual_host_compatibility.py`
- Create: `scripts/validate_dual_host_compatibility.py`

**Interfaces:**

- `parse_skill_frontmatter(path: Path) -> dict[str, str]`
- `parse_top_level_yaml_scalars(path: Path) -> dict[str, str]`
- `validate_skill(skill_dir: Path) -> list[str]`
- `validate_plugin(plugin_dir: Path) -> list[str]`
- `validate_repository(skills_root: Path, plugins_root: Path) -> list[str]`
- CLI: `--all`, `--skill PATH`, `--plugin PATH`, optional `--json`.

- [ ] **Step 1: Write failing temporary-fixture tests**

The test file must use these concrete fixture helpers, then mutate one condition per test:

~~~python
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from validate_dual_host_compatibility import (
    validate_plugin,
    validate_repository,
    validate_skill,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "validate_dual_host_compatibility.py"


def write_skill(root, name, description="Shared workflow."):
    skill_dir = root / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n# Skill\n",
        encoding="utf-8",
    )
    return skill_dir


def write_plugin(root, name="sample-plugin"):
    plugin_dir = root / name
    (plugin_dir / ".codex-plugin").mkdir(parents=True)
    (plugin_dir / "skills" / name).mkdir(parents=True)
    (plugin_dir / ".codex-plugin" / "plugin.json").write_text(
        json.dumps(
            {"name": name, "version": "1.0.0", "description": "Codex package."}
        ),
        encoding="utf-8",
    )
    (plugin_dir / "plugin.yaml").write_text(
        "manifest_version: 1\n"
        f"name: {name}\n"
        "version: 1.0.0\n"
        "description: Hermes package.\n"
        "kind: standalone\n",
        encoding="utf-8",
    )
    (plugin_dir / "skills" / name / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Bundled workflow.\n---\n",
        encoding="utf-8",
    )
    (plugin_dir / "__init__.py").write_text(
        "def register(ctx):\n"
        f"    ctx.register_skill({name!r}, 'skills/{name}/SKILL.md')\n",
        encoding="utf-8",
    )
    return plugin_dir
~~~

~~~python
class DualHostCompatibilityTests(unittest.TestCase):
    def test_valid_repository_passes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skills_root = root / "skills"
            plugins_root = root / "plugins"
            write_skill(skills_root, "sample-skill")
            write_plugin(plugins_root)
            self.assertEqual([], validate_repository(skills_root, plugins_root))

    def test_skill_contract_failures(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            missing = root / "missing"
            missing.mkdir()
            self.assertIn("missing/SKILL.md is required", validate_skill(missing))
            mismatch = write_skill(root, "folder-name", description="")
            path = mismatch / "SKILL.md"
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "name: folder-name", "name: another-name"
                ),
                encoding="utf-8",
            )
            errors = validate_skill(mismatch)
            self.assertIn(
                "folder-name: frontmatter name must equal directory name", errors
            )
            self.assertIn(
                "folder-name: frontmatter description must be non-empty", errors
            )

    def test_separate_description_md_discovery_file_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = write_skill(Path(tmpdir), "sample-skill")
            (skill_dir / "description.md").write_text(
                "Wrong entrypoint.", encoding="utf-8"
            )
            self.assertIn(
                "sample-skill: SKILL.md must not depend on description.md for discovery",
                validate_skill(skill_dir),
            )

    def test_plugin_identity_and_registration_failures(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = write_plugin(Path(tmpdir))
            codex_path = plugin_dir / ".codex-plugin" / "plugin.json"
            codex = json.loads(codex_path.read_text(encoding="utf-8"))
            codex["version"] = "2.0.0"
            codex_path.write_text(json.dumps(codex), encoding="utf-8")
            (plugin_dir / "__init__.py").write_text(
                "def register(ctx):\n    pass\n", encoding="utf-8"
            )
            errors = validate_plugin(plugin_dir)
            self.assertIn(
                "sample-plugin: Codex and Hermes versions must match", errors
            )
            self.assertIn(
                "sample-plugin: bundled skills require ctx.register_skill(...)", errors
            )

    def test_cli_json_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skills_root = root / "skills"
            plugins_root = root / "plugins"
            (skills_root / "bad-skill").mkdir(parents=True)
            plugins_root.mkdir()
            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--all",
                    "--skills-root",
                    str(skills_root),
                    "--plugins-root",
                    str(plugins_root),
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(1, result.returncode)
            self.assertFalse(payload["ok"])
            self.assertIn("bad-skill/SKILL.md is required", payload["errors"])


if __name__ == "__main__":
    unittest.main()
~~~

Run:

~~~bash
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/test_validate_dual_host_compatibility.py
~~~

Expected: import failure because the validator does not exist.

- [ ] **Step 2: Implement the validator**

Implementation requirements:

1. Parse only top-level `name` and `description` from skill frontmatter.
2. Parse only top-level scalar keys from `plugin.yaml`; do not add PyYAML.
3. Validate skill entrypoint, directory/name equality, non-empty description, and absence of a separate `description.md` discovery file. Do not scan prose for the filename.
4. Validate both plugin manifests, exact name/version equality, non-empty descriptions, `manifest_version: 1`, non-empty `kind`, and `register(ctx)`.
5. Use Python `ast` to find `register` and `ctx.register_skill(...)` when bundled skill entrypoints exist.
6. Print `{"ok": bool, "errors": list}` under `--json`; otherwise print errors to stderr and return 1.
7. Iterate every direct child directory of `skills/` and `plugins/` under `--all`.

Start the file with:

~~~python
#!/usr/bin/env python3
"""Validate Codex/Hermes repository compatibility without live mutations."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILLS_ROOT = REPO_ROOT / "skills"
DEFAULT_PLUGINS_ROOT = REPO_ROOT / "plugins"
~~~

Core validation body:

~~~python
def validate_skill(skill_dir):
    entrypoint = skill_dir / "SKILL.md"
    if not entrypoint.is_file():
        return [f"{skill_dir.name}/SKILL.md is required"]
    fields = parse_skill_frontmatter(entrypoint)
    errors = []
    if fields.get("name", "").strip() != skill_dir.name:
        errors.append(f"{skill_dir.name}: frontmatter name must equal directory name")
    if not fields.get("description", "").strip():
        errors.append(f"{skill_dir.name}: frontmatter description must be non-empty")
    if (skill_dir / "description.md").exists():
        errors.append(
            f"{skill_dir.name}: SKILL.md must not depend on description.md for discovery"
        )
    return errors
~~~

Use `ast.parse`, locate a top-level `FunctionDef` named `register`, and walk it for a `Call` whose function is an `Attribute` named `register_skill`.

Implement the remaining helpers and CLI with these exact bodies:

~~~python
def _unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_skill_frontmatter(path):
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
        parsed[key.strip()] = _unquote(value)
    return parsed


def parse_top_level_yaml_scalars(path):
    parsed = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line or line[:1].isspace() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        parsed[key.strip()] = _unquote(value)
    return parsed


def _register_function(path):
    try:
        module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError):
        return None
    return next(
        (
            node
            for node in module.body
            if isinstance(node, ast.FunctionDef) and node.name == "register"
        ),
        None,
    )


def _calls_register_skill(function):
    return any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "register_skill"
        for node in ast.walk(function)
    )


def validate_plugin(plugin_dir):
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
    hermes = parse_top_level_yaml_scalars(hermes_path)
    if codex.get("name") != name or hermes.get("name") != name:
        errors.append(f"{name}: manifest names must equal directory name")
    if codex.get("version") != hermes.get("version"):
        errors.append(f"{name}: Codex and Hermes versions must match")
    if not str(codex.get("description", "")).strip():
        errors.append(f"{name}: Codex description must be non-empty")
    if not hermes.get("description", "").strip():
        errors.append(f"{name}: Hermes description must be non-empty")
    if hermes.get("manifest_version") != "1":
        errors.append(f"{name}: Hermes manifest_version must be 1")
    if not hermes.get("kind", "").strip():
        errors.append(f"{name}: Hermes kind must be non-empty")
    register = _register_function(entrypoint)
    if register is None:
        errors.append(f"{name}: __init__.py must define register(ctx)")
        return errors
    skills_dir = plugin_dir / "skills"
    bundled = list(skills_dir.rglob("SKILL.md")) if skills_dir.is_dir() else []
    if bundled and not _calls_register_skill(register):
        errors.append(f"{name}: bundled skills require ctx.register_skill(...)")
    return errors


def validate_repository(skills_root, plugins_root):
    errors = []
    if skills_root.is_dir():
        for path in sorted(item for item in skills_root.iterdir() if item.is_dir()):
            errors.extend(validate_skill(path))
    if plugins_root.is_dir():
        for path in sorted(item for item in plugins_root.iterdir() if item.is_dir()):
            errors.extend(validate_plugin(path))
    return errors
~~~

Use this exact CLI:

~~~python
def parser():
    result = argparse.ArgumentParser(description=__doc__)
    target = result.add_mutually_exclusive_group(required=True)
    target.add_argument("--all", action="store_true")
    target.add_argument("--skill", type=Path)
    target.add_argument("--plugin", type=Path)
    result.add_argument("--skills-root", type=Path, default=DEFAULT_SKILLS_ROOT)
    result.add_argument("--plugins-root", type=Path, default=DEFAULT_PLUGINS_ROOT)
    result.add_argument("--json", action="store_true")
    return result


def main(argv=None):
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
~~~

- [ ] **Step 3: Run tests, repository validation, and targeted modes**

~~~bash
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/test_validate_dual_host_compatibility.py
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_dual_host_compatibility.py --all
python3 scripts/validate_dual_host_compatibility.py --skill skills/decide-in-order
python3 scripts/validate_dual_host_compatibility.py --plugin plugins/task-management
~~~

Expected: 5 tests OK and three successful validations.

- [ ] **Step 4: Commit**

~~~bash
git add scripts/validate_dual_host_compatibility.py scripts/test_validate_dual_host_compatibility.py
git commit -m "Validate dual-host repository compatibility"
~~~

Expected: one validator/test commit.

## Task 3: Existing skill and plugin distribution contract

**Files:**

- Modify: `plugins/task-management/README.md`
- Modify: `plugins/task-management/tests/test_hermes_plugin_manifest.py`
- Modify: `skills/decide-in-order/tests/test_skill_contract.py`

**Interfaces:**

- Consumes: Hermes GitHub identifier shape `owner/repo/skills/my-workflow` and the existing unavailable-companion policy.
- Produces: `hermes skills install omitsuhashi/skills/skills/decide-in-order`, read-only visibility checks, plugin version-match rule, and fallback wording.

- [ ] **Step 1: Extend artifact-specific tests first**

Add to the existing Hermes README contract test:

~~~python
self.assertIn(
    "hermes skills install omitsuhashi/skills/skills/decide-in-order",
    text,
)
self.assertIn("hermes skills list", text)
self.assertIn("hermes plugins list --plain --no-bundled", text)
self.assertIn("must match `plugin.yaml`", text)
self.assertIn("Mechanical task operations continue", text)
~~~

Add to `skills/decide-in-order/tests/test_skill_contract.py`:

~~~python
def test_hermes_uses_the_standard_skill_entrypoint(self):
    frontmatter = self.skill_text.split("---", 2)[1]
    self.assertIn("name: decide-in-order", frontmatter)
    self.assertIn("description:", frontmatter)
    self.assertFalse((SKILL_DIR / "description.md").exists())
    self.assertTrue(OPENAI_YAML.is_file())
~~~

- [ ] **Step 2: Run targeted tests and observe the documentation failure**

~~~bash
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 plugins/task-management/tests/test_hermes_plugin_manifest.py
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/decide-in-order/tests/test_skill_contract.py
~~~

Expected: task-management fails on the new README assertions; decide-in-order passes and fixes the no-`description.md` contract.

- [ ] **Step 3: Add the companion section to the plugin README**

Insert after `## Hermes Install`:

~~~markdown
### Optional decision companion

The plugin bundles `task-management`, but `$decide-in-order` remains a standalone
skill and is not copied into this plugin. Install it separately when deep
prioritization, continuation, or review support is required:

    hermes skills install omitsuhashi/skills/skills/decide-in-order
    hermes skills list

Confirm that `decide-in-order` appears for the target profile. If it is absent,
Mechanical task operations continue, but the plugin must not claim that deep
decision support ran; severe irreversible decisions still stop for human review.

Repository compatibility does not prove the loaded plugin version. Before an
approved live smoke, run:

    hermes plugins list --plain --no-bundled

The enabled `task-management` version must match `plugin.yaml`. Refresh with the
documented force-install flow when the loaded version is stale.
~~~

- [ ] **Step 4: Run targeted and full verification**

~~~bash
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/decide-in-order/tests/test_skill_contract.py
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 plugins/task-management/tests/test_hermes_plugin_manifest.py
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 plugins/task-management/scripts/smoke_test_hermes_read.py
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/decide-in-order
python3 /Users/omitsuhashi/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/task-management
~~~

Expected: targeted tests, full plugin suite, hermetic smoke, and both creator validators pass. No live profile is changed.

- [ ] **Step 5: Commit**

~~~bash
git add plugins/task-management/README.md plugins/task-management/tests/test_hermes_plugin_manifest.py skills/decide-in-order/tests/test_skill_contract.py
git commit -m "Document Hermes companion discovery"
~~~

Expected: one current-artifact contract commit.

## Task 4: CI enforcement and durable evidence

**Files:**

- Modify: `.github/workflows/skill-architecture.yml`
- Modify: `knowledge/wiki/syntheses/hermes-dual-host-authoring-contract-design.md`
- Modify: `knowledge/index.md`
- Modify: `knowledge/log.md`

**Interfaces:**

- Consumes: Tasks 1–3 tests and `scripts/validate_dual_host_compatibility.py --all`.
- Produces: Python 3.9 / 3.12 CI enforcement, final local evidence, and an explicit live-state non-guarantee.

- [ ] **Step 1: Add CI steps**

After `Validate skill context`, add:

~~~yaml
      - name: Test dual-host authoring guidance
        run: PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/test_dual_host_authoring_guidance.py

      - name: Test dual-host compatibility validator
        run: PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/test_validate_dual_host_compatibility.py

      - name: Validate dual-host compatibility
        run: PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_dual_host_compatibility.py --all
~~~

Do not add live Hermes installation or profile mutation to CI.

- [ ] **Step 2: Run the full local matrix**

~~~bash
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/test_dual_host_authoring_guidance.py
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/test_validate_dual_host_compatibility.py
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_dual_host_compatibility.py --all
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_skill_context.py --all
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/decide-in-order/tests
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 plugins/task-management/scripts/smoke_test_hermes_read.py
git diff --check
~~~

Expected: every command exits 0. Record actual counts rather than predicted counts.

- [ ] **Step 3: Inspect live state read-only**

~~~bash
hermes skills list
hermes plugins list --plain --no-bundled
~~~

Expected in the current pre-install environment: `decide-in-order` may remain absent and `task-management` may remain at `0.1.0`. Record this as distribution drift, not repository failure. Do not install, update, enable, or edit `~/.hermes/config.yaml`.

- [ ] **Step 4: Update durable evidence**

After all checks pass:

- mark the design implemented / locally verified;
- add actual test counts and commands;
- record whether live skill visibility and plugin version remain unchanged;
- keep live install / refresh as a separate follow-up;
- keep the design and this plan exactly once in `knowledge/index.md`;
- append one `implementation | Codex / Hermes dual-host authoring contract` entry to `knowledge/log.md`.

- [ ] **Step 5: Verify wiki, Goal tracking policy, and diff hygiene**

~~~bash
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests
git check-ignore -v goals/sample.json
git ls-files goals
git status --short
git diff --check
~~~

Expected: wiki tests pass; `goals/sample.json` is not ignored by a new rule; existing tracked Goal files remain visible; only intended files are modified.

- [ ] **Step 6: Commit**

~~~bash
git add .github/workflows/skill-architecture.yml knowledge/wiki/syntheses/hermes-dual-host-authoring-contract-design.md knowledge/index.md knowledge/log.md
git commit -m "Enforce dual-host compatibility in CI"
~~~

Expected: final CI/evidence commit.

## Final Review Checklist

- [ ] Root guidance remains a thin router.
- [ ] No `description.md` was created.
- [ ] No standalone skill source was copied into a plugin.
- [ ] Validator uses Python 3.9-compatible standard library only.
- [ ] Validator never claims install or live load success.
- [ ] Plugin-specific registration and hermetic smoke remain authoritative for runtime behavior.
- [ ] Tool vocabulary and response quality were not converted into brittle generic scoring.
- [ ] Live Hermes profile, config, credential, plugin installation, and skill installation were not changed.
- [ ] Creator validators, repository tests, architecture/context validators, wiki tests, and `git diff --check` pass.

## 関連ページ

- [Codex / Hermes Dual-host Authoring Contract 設計](hermes-dual-host-authoring-contract-design.md) — 本計画の承認済み要求と非目標。
- [Decide In Order Skill 設計](decide-in-order-skill-design.md) — standalone skill と task-management companion の責務境界。
- [Portfolio OS Task Backend Plugin Skill Spec](portfolio-os-task-backend-plugin-skill-spec.md) — task-management の Codex / Hermes runtime 境界。

## 出典

- [Hermes Agent Skills System](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/skills.md)
- [Build a Hermes Plugin](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/guides/build-a-hermes-plugin.md)
- [Codex / Hermes Dual-host Authoring Contract 設計](hermes-dual-host-authoring-contract-design.md)
