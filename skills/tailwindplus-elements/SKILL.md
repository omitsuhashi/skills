---
name: tailwindplus-elements
description: Install or integrate @tailwindplus/elements, or look up Tailwind Plus el-* component APIs and behavior. Use for HTML or React integration, not generic Tailwind CSS questions.
---

# Tailwind Plus Elements

## Contract

- **Inputs:** the integration question or requested change, relevant snippets or project files, and the component involved.
- **Outputs:** a focused explanation or the requested integration change, with verification results and any remaining limits.
- **Required capabilities:** reference reading; project inspection and editing for implementation; package installation and browser execution only when the requested work requires them. If a capability is unavailable, provide the supported guidance and identify the operation or verification left undone.

## Quick Workflow

1. Infer CDN, npm, or React integration from the project and request. Preserve the existing mode unless a change is requested or necessary for correctness.
2. Identify the target component or primitive before loading references.
3. Read only the matching file in `references/`.
4. In React, prefer the React exports from `@tailwindplus/elements/react` over raw custom elements.
5. If adding DOM behavior around these components, wait for `elements:ready` unless the custom element is already registered.
6. For implementation, verify the affected interaction with available project checks or a browser, including relevant keyboard and focus behavior. Report unavailable checks; API lookup alone does not require building a demo or installing packages.

## Reference Map

- `references/getting-started.md`
  Covers installation, browser support, React usage, and `elements:ready`.
- `references/form-and-choice-components.md`
  Covers Autocomplete, Select, and shared choice primitives.
- `references/overlay-and-disclosure-components.md`
  Covers Dialog, Disclosure, Dropdown menu, and Popover.
- `references/utility-and-navigation-components.md`
  Covers Command palette, Copy button, and Tabs.

## Common Mistakes

- Treating `el-options` width or anchor behavior as automatic. Many layouts still need explicit classes or CSS variables.
- Mixing up similar primitives. `el-options` serves Autocomplete and Select, while `el-menu` belongs to Dropdown.
