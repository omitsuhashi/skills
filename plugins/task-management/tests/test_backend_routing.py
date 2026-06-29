import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
CONFIG_PATH = REPO_ROOT / "plugins/task-management/config/task-backends.example.toml"
SKILL_PATH = REPO_ROOT / "plugins/task-management/skills/task-management/SKILL.md"
REFERENCE_PATH = (
    REPO_ROOT
    / "plugins/task-management/skills/task-management/references/backend-routing.md"
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

    def test_github_projects_mcp_is_default_route_without_project_target(self):
        config = self.load_config()

        self.assertEqual(config["default_backend"], "github_projects_mcp")
        route = config["backends"]["github_projects_mcp"]

        self.assertEqual(route["kind"], "mcp")
        self.assertEqual(route["connection_ref"], "github-projects")
        self.assertEqual(route["capability"], "project_management")

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

    def test_route_config_allows_only_field_overrides_not_destination_targets(self):
        config = self.load_config()
        route = config["backends"]["github_projects_mcp"]
        field_overrides = route.get("field_overrides", {})

        self.assertIsInstance(field_overrides, dict)

        forbidden_destination_fragments = (
            "owner",
            "project_number",
            "repository",
            "repo",
            "token",
            "credential",
            "secret",
        )
        for key, value in field_overrides.items():
            haystack = f"{key} {value}".lower()
            for fragment in forbidden_destination_fragments:
                self.assertNotIn(fragment, haystack)


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

    def test_reference_separates_route_registry_from_destination_input(self):
        reference = self.load_reference()

        self.assertIn("Route Registry", reference)
        self.assertIn("Destination Input", reference)
        self.assertIn("TaskBackendDestination", reference)
        self.assertIn("destination_ref", reference)
        self.assertIn("content_target_ref", reference)
        self.assertIn("opaque references", reference)
        self.assertIn("first backend", reference)
        self.assertIn("not a permanent architecture", reference)

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
