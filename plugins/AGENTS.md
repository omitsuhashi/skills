# Plugin authoring contract

- Plugins may target one runtime.
- Do not add another runtime package solely for compatibility.
- Keep the selected runtime's manifest and registration aligned through
  plugin-specific tests.
- Treat a standalone companion skill as a separate install prerequisite. Do not copy its source into the plugin. Document behavior when unavailable.
- For approved live verification, confirm enablement and version in the selected
  runtime, then run the plugin smoke.
- Do not mutate a live profile, marketplace, credential, or install state during
  ordinary validation.
- Run the plugin-creator validator before handoff.
