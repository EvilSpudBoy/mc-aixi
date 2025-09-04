# Repository Guidelines

## Project Structure & Module Organization
- src/: C++ sources and headers (.cpp/.hpp). Build outputs (.o/.d) are ignored.
- conf/: Example configuration files for each environment (e.g., tictactoe.conf).
- log/: Run logs written by the agent (CSV). Safe to delete/regenerate.
- graph/: Generated plots from logs (via graph.py).
- doc/: Generated documentation (see doc/html/index.html).
- tutorial/: Paper/tutorial assets. uml/: Diagrams. Makefile at repo root builds the binary `aixi`.

## Build, Test, and Development Commands
- make: Compile all sources and produce `./aixi` (g++ -O3 -Wall -g).
- make clean: Remove binary and intermediate objects.
- ./aixi conf/<env>.conf log/<name>.csv: Run the agent with a config and write a CSV log.
  Example: `./aixi conf/tictactoe.conf log/tictactoe.csv`
- Optional tests: Makefile includes `test-predict` and `test-agent` targets that expect `tests/test-*.o`.
  To add a test: `g++ -g -I src -c tests/test-foo.cpp -o tests/test-foo.o` and mirror existing targets.

## Coding Style & Naming Conventions
- Language: Portable C++ built with g++. Prefer no new dependencies.
- Indentation: Tabs (match existing files). Keep lines concise and readable.
- Filenames: lower-case; headers `.hpp`, sources `.cpp` (e.g., maze.hpp/maze.cpp).
- Types/Classes: UpperCamelCase (Agent, Environment). Functions/methods: lowerCamelCase (modelUpdate, search).
- Type aliases: suffix `_t` (age_t, reward_t). Keep header/source pairs in sync.

## Testing Guidelines
- No formal framework is bundled. Add lightweight tests under `tests/` and wire targets in the Makefile.
- Name tests `test-<topic>.cpp` and keep them self-contained. Aim for warnings-free builds (`-Wall`).
- For behavioral checks, run environments with fixed `random-seed` and compare log summaries.

## Commit & Pull Request Guidelines
- Commits: Imperative, concise subject (e.g., “add imagetrainer environment”), optional body for rationale.
- Scope: Small, single-purpose changes. Update docs/configs when behavior changes.
- PRs: Include description, affected modules, run command used, and sample log excerpt or screenshot of graphs.
- Hygiene: Ensure `make` succeeds; do not commit `aixi`, `src/*.o`, `src/*.d`, or large logs/graphs.

## Configuration & Logs
- Use `conf/*.conf` to select the environment (`environment=tictactoe|maze|pacman|...`) and parameters (e.g., `random-seed`, `exploration`).
- Always pass an explicit log path when running to capture results; generate plots with `python graph.py` (outputs under `graph/<logfile>/`).
