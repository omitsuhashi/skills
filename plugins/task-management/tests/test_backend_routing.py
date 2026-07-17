import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
CONFIG_PATH = REPO_ROOT / "plugins/task-management/config/task-backends.example.toml"
LOCAL_SNAPSHOT_EXAMPLE_PATH = (
    REPO_ROOT / "plugins/task-management/examples/local-task-snapshot.example.json"
)
README_PATH = REPO_ROOT / "plugins/task-management/README.md"
SKILL_PATH = REPO_ROOT / "plugins/task-management/skills/task-management/SKILL.md"
REFERENCE_PATH = (
    REPO_ROOT
    / "plugins/task-management/skills/task-management/references/backend-routing.md"
)
ROUTING_FLOW_PATH = (
    REPO_ROOT
    / "plugins/task-management/skills/task-management/references/routing-flow.md"
)
TASK_CONTRACTS_PATH = (
    REPO_ROOT
    / "plugins/task-management/skills/task-management/references/task-contracts.md"
)
TASK_READ_ADAPTER_PATH = (
    REPO_ROOT
    / "plugins/task-management/skills/task-management/references/task-read-adapter.md"
)


def parse_example_toml(text):
    parsed = {}
    current = parsed
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            current = parsed
            for part in line.strip("[]").split("."):
                current = current.setdefault(part, {})
            continue
        key, value = [part.strip() for part in line.split("=", 1)]
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        current[key] = value
    return parsed


class BackendRoutingConfigTests(unittest.TestCase):
    def load_config(self):
        return parse_example_toml(CONFIG_PATH.read_text(encoding="utf-8"))

    def test_operator_example_uses_external_default_read_route(self):
        config = self.load_config()

        self.assertEqual(config["contract_version"], "1")
        self.assertEqual(config["default_backend"], "remote_tasks")
        route = config["backends"]["remote_tasks"]

        self.assertIn(route["kind"], {"mcp", "plugin"})
        self.assertEqual(route["capability"], "task_read")
        if route["kind"] == "mcp":
            self.assertEqual(route["tool_name"], "mcp__task_backend__task_query")
        else:
            self.assertEqual(
                route["tool_name"], "task_adapter__provider__task_query"
            )

        example_text = CONFIG_PATH.read_text(encoding="utf-8")
        self.assertNotIn('kind = "local_json"', example_text)
        self.assertNotIn("read_root", example_text)
        self.assertNotIn("source_path", example_text)
        self.assertNotIn("local-task-snapshot.example.json", example_text)

        forbidden_keys = {
            "owner",
            "org",
            "organization",
            "project",
            "project_number",
            "repository",
            "repo",
            "token",
            "credential",
            "secret",
        }
        self.assertTrue(forbidden_keys.isdisjoint(route.keys()))

    def test_route_config_maps_only_logical_destination_refs(self):
        config = self.load_config()
        route = config["backends"][config["default_backend"]]
        destination = route["destinations"]["default"]

        self.assertEqual("tasks:default", destination["public_ref"])
        self.assertEqual("tasks:default", destination["provider_ref"])

        forbidden_destination_fragments = (
            "owner",
            "project_number",
            "repository",
            "repo",
            "token",
            "credential",
            "secret",
        )
        for key, value in destination.items():
            haystack = f"{key} {value}".lower()
            for fragment in forbidden_destination_fragments:
                self.assertNotIn(fragment, haystack)

    def test_operator_examples_do_not_publish_a_local_task_snapshot(self):
        self.assertFalse(LOCAL_SNAPSHOT_EXAMPLE_PATH.exists())


class BackendRoutingReferenceTests(unittest.TestCase):
    def load_reference(self):
        return REFERENCE_PATH.read_text(encoding="utf-8")

    def test_skill_entrypoint_reaches_routing_and_github_mcp_references(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")

        for reference in (
            "references/task-contracts.md",
            "references/backend-routing.md",
            "references/github-mcp-projects.md",
            "references/hermes-mcp-governance.md",
        ):
            self.assertIn(reference, skill)

    def test_skill_limits_portfolio_os_evidence_to_generic_plugin_lifecycle(self):
        skill = " ".join(SKILL_PATH.read_text(encoding="utf-8").split())

        self.assertIn(
            "Portfolio OS must not own task route, task data, task result, or "
            "task-specific evidence. It may keep only generic plugin selection, "
            "native install, manifest identity / required-export verification, "
            "and generic profile enablement evidence.",
            skill,
        )
        self.assertNotIn(
            "source trail, routing rationale, draft previews, backend references, "
            "and decision logs",
            skill,
        )

    def test_reference_separates_route_registry_from_destination_input(self):
        reference = self.load_reference()
        normalized = " ".join(reference.split())

        self.assertIn("Route Registry", normalized)
        self.assertIn("Destination Input", normalized)
        self.assertIn("TaskBackendDestination", normalized)
        self.assertIn("destination_ref", normalized)
        self.assertIn("content_target_ref", normalized)
        self.assertIn("opaque references", normalized)
        self.assertIn("test and smoke fixture", normalized)
        self.assertIn("no implicit GitHub fallback", normalized)

    def test_operator_docs_limit_local_json_to_plugin_owned_fixtures(self):
        readme = README_PATH.read_text(encoding="utf-8")
        skill = SKILL_PATH.read_text(encoding="utf-8")
        routing = self.load_reference()
        flow = ROUTING_FLOW_PATH.read_text(encoding="utf-8")
        contracts = TASK_CONTRACTS_PATH.read_text(encoding="utf-8")
        adapter = TASK_READ_ADAPTER_PATH.read_text(encoding="utf-8")
        normalized_skill = " ".join(skill.split())
        normalized_routing = " ".join(routing.split())
        normalized_contracts = " ".join(contracts.split())
        normalized_adapter = " ".join(adapter.split())

        self.assertIn("not a normal runtime backend", readme)
        self.assertNotIn("local-task-snapshot.example.json", readme)
        self.assertNotIn("local bootstrap read snapshot", skill)
        self.assertIn(
            "`local_json` is reserved for plugin-owned test and smoke fixtures",
            normalized_skill,
        )
        self.assertIn("test and smoke fixture", normalized_routing)
        self.assertIn("test-only `local_json`", flow)
        self.assertNotIn('route -->|"kind = local_json"|', flow)
        self.assertNotIn("SamePublicCall --> LocalSnapshot", flow)
        self.assertIn(
            "temporary plugin-owned test and smoke fixture", normalized_contracts
        )
        self.assertIn(
            "is not an initial reference read route", normalized_contracts
        )
        self.assertIn("not an operator-facing runtime backend", normalized_adapter)

    def test_reference_forbids_concrete_github_targets_in_plugin_config(self):
        reference = " ".join(self.load_reference().split())

        required_phrases = [
            "must not decompose or store GitHub owner",
            "project number",
            "repository",
            "token",
            "field ID",
            "option ID",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, reference)


if __name__ == "__main__":
    unittest.main()
