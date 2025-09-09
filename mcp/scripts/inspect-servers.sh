#!/usr/bin/env bash
set -euo pipefail

die() { echo "[inspect-servers] $*" >&2; exit 1; }
has() { command -v "$1" >/dev/null 2>&1; }

check_node() {
  if ! has npx; then
    die "npx is required. Install Node.js >= 22 and try again."
  fi
  if has node; then
    echo "[inspect-servers] node $(node -v)"
  else
    echo "[inspect-servers] Warning: node not found in PATH"
  fi
}

run_inspector() {
  local server_name=$1
  local server_dir=$2
  local entry=$3

  if [[ ! -d "$server_dir" ]]; then
    echo "[inspect-servers] Skip $server_name: dir not found: $server_dir"
    return 0
  fi

  local cmd
  local -a args

  if has uv; then
    cmd="uv"
    args=("--directory" "$server_dir" "run" "$entry")
  elif [[ -x "$server_dir/.venv/bin/python" ]]; then
    cmd="$server_dir/.venv/bin/python"
    args=("$server_dir/$entry")
  else
    cmd="python"
    args=("$server_dir/$entry")
  fi

  echo "[inspect-servers] Checking $server_name (command: $cmd ${args[*]})"
  npx @modelcontextprotocol/inspector --cli --transport stdio "$cmd" "${args[@]}" --method tools/list || \
    echo "[inspect-servers] Warning: tools/list failed for $server_name"
}

main() {
  check_node
  run_inspector "mcp-hello"       "$(dirname "$0")/../tools/mcp-hello"       "hello.py"
  run_inspector "mcp-aixi-tools"  "$(dirname "$0")/../tools/mcp-aixi-tools"  "server.py"

  # Optional: quick tool calls if hello server available
  if has uv && [[ -d "$(dirname "$0")/../tools/mcp-hello" ]]; then
    echo "[inspect-servers] (optional) Try hello tool"
    npx @modelcontextprotocol/inspector --cli --transport stdio \
      uv --directory "$(dirname "$0")/../tools/mcp-hello" run hello.py \
      --method tools/call --tool-name hello --tool-arg name=World || true
  fi
  echo "[inspect-servers] Done"
}

main "$@"

