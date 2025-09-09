# AGENTS.md — Xcode Project (scope: xcode/mc-aixi/)

This file applies to everything under `xcode/mc-aixi/`.

Purpose
- Provide an Xcode workspace for working with the C++ sources in `../../src/`.
- Keep the Xcode setup in sync with the canonical Makefile build.

Build & Run
- Canonical build remains `make` at the repo root (`g++ -O3 -Wall -g`).
- Xcode project should mirror those flags for parity.
- If headers aren’t found, ensure Header Search Paths include `$(SRCROOT)/../../src`.

Adding/Refactoring Code
- Add new `.hpp/.cpp` under the repo `src/` directory; then reference them in Xcode groups.
- Keep filenames lower-case; classes in UpperCamelCase; methods lowerCamelCase.
- Use tabs for indentation to match the codebase.

Keep In Sync
- When changing build settings in Xcode (optimizations, warnings), mirror changes in the root Makefile if appropriate, or document why they differ.
- Adding/removing sources in Xcode should not diverge from what `make` builds.

Do Not Commit
- User/host-specific state or derived data. These are already ignored:
  - `**/*.xcuserdata/`, `**/*.xcuserstate`, `**/DerivedData/`
- Any build outputs or local caches.

Testing
- Primary tests use the root `Makefile` optional targets and ad-hoc g++ compiles under `tests/`.
- Keep Xcode schemes minimal; do not introduce test frameworks here unless agreed.

Hygiene
- Keep the project tidy: clear, minimal groups mirroring `src/` layout.
- Avoid adding large assets or generated files to the project.

