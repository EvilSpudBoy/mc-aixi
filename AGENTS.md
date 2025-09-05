# Repository Guidelines

## Project Structure & Module Organization
- src/: C++ sources and headers (.cpp/.hpp). Build outputs (.o/.d) are ignored.
- conf/: Example configuration files for each environment (e.g., tictactoe.conf).
- log/: Run logs written by the agent (CSV). Safe to delete/regenerate.
- graph/: Generated plots from logs (via graph.py).
- doc/: Generated documentation (see doc/html/index.html).
- tutorial/: Paper/tutorial assets. uml/: Diagrams. Makefile at repo root builds the binary `aixi`.
- mcp/tools/: MCP development area (Python servers/tools). Example: `mcp-hello`.

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

## MCP Tools (Python)

### Location
- `mcp/tools/mcp-hello/`: Minimal MCP server using FastMCP exposing:
  - `hello(name: str) -> str`
  - `add(a: float, b: float) -> float`
  - `get_alerts(state: str) -> str` (US NWS alerts)
  - `get_forecast(latitude: float, longitude: float) -> str` (US NWS forecast)

### Requirements
- Python 3.10+
- Dependencies: `mcp[cli] >= 1.2.0`, `httpx`

### Setup
Using uv (recommended):

```bash
cd mcp/tools/mcp-hello
uv venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .
```

Using pip:

```bash
cd mcp/tools/mcp-hello
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

### Run (STDIO server)

```bash
python hello.py
# or
uv run hello.py
```

### Test with MCP Inspector (no install)

```bash
npx @modelcontextprotocol/inspector python hello.py
```

- Choose STDIO transport. Tools available: `hello`, `add`, `get_alerts`, `get_forecast`.
- Inspector requires Node.js >= 22.7.5. If your Node is older, upgrade via `nvm`, `fnm`, or Volta.

CLI examples (Inspector):

```bash
cd mcp/tools/mcp-hello
. .venv/bin/activate

# List tools
npx @modelcontextprotocol/inspector --cli --transport stdio .venv/bin/python hello.py --method tools/list

# Call hello
npx @modelcontextprotocol/inspector --cli --transport stdio .venv/bin/python hello.py \
  --method tools/call --tool-name hello --tool-arg name=World

# Call get_alerts
npx @modelcontextprotocol/inspector --cli --transport stdio .venv/bin/python hello.py \
  --method tools/call --tool-name get_alerts --tool-arg state=CA

# Call get_forecast
npx @modelcontextprotocol/inspector --cli --transport stdio .venv/bin/python hello.py \
  --method tools/call --tool-name get_forecast \
  --tool-arg latitude=38.5816 --tool-arg longitude=-121.4944
```

Quick upgrade with nvm:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm install 22
nvm use 22
node -v && npm -v
```

### Claude Desktop integration
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-hello": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/mcp/tools/mcp-hello",
        "run",
        "hello.py"
      ]
    }
  }
}
```

### Notes
- STDIO servers must not write to stdout (no `print`); use logging to stderr.
- Weather tools query `api.weather.gov` and only support US locations.
