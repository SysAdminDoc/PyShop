# Changelog

## PyShop v0.1.2 - 2026-06-27

- Extracted layer state, bounded history, selection contour generation, and blend-mode compositing into `pyshop.core`.
- Added focused core tests for layer copies, history snapshots, blend immutability, and selection path generation.

## PyShop v0.1.1 - 2026-06-27

- Added the initial `pyshop/` package skeleton with core, tools, panels, filters, ui, and resources namespaces.
- Moved app identity and icon discovery into `pyshop.app_info` while preserving the existing desktop entrypoint.

## PyShop v0.1.0 - 2026-06-27

- Fixed the top-level Qt import syntax error that prevented the app from compiling.
- Added explicit runtime and development dependency manifests.
- Added a pytest import smoke test that verifies the module imports without launching a GUI.
- Documented supported Python/PyQt versions and the manual desktop QA checklist.
