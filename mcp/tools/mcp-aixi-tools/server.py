"""
MCP server exposing repo-specific tools for mc-aixi.

Transport: stdio (launch as a subprocess from an MCP-compatible host).

Tools provided:
- list_envs(): List available conf files under conf/.
- build(target?): Run `make` in repo root; return a concise summary.
- run_agent(conf, log_path?): Run `./aixi <conf> <log>`; auto-build if missing.
- graph_log(log_file): Run `python3 graph.py <log_file>`; return output dir.
- summarize_log(log_file): Compute quick metrics from a CSV-like .log file.
- search_code(query, path?): Lightweight code search within the repo.

Notes:
- Avoid printing to stdout; MCP stdio uses stdout for protocol messages.
- This server depends only on Python stdlib.
"""

from __future__ import annotations

import csv
import io
import os
import re
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

# FastMCP is referenced in the accompanying MCP PDF and Python SDKs.
from mcp.server.fastmcp import FastMCP  # type: ignore


def _detect_repo_root() -> Path:
    here = Path(__file__).resolve()
    for base in here.parents:
        if (base / "conf").is_dir() and (base / "src").is_dir():
            return base
    # Fallback: assume repo layout and step up three levels
    # mcp/tools/mcp-aixi-tools/server.py -> repo root is parents[3]
    try:
        return here.parents[3]
    except IndexError:
        return here.parent


REPO_ROOT = _detect_repo_root()
CONF_DIR = REPO_ROOT / "conf"
SRC_DIR = REPO_ROOT / "src"
LOG_DIR = REPO_ROOT / "log"
GRAPH_PY = REPO_ROOT / "graph.py"
AIXI_BIN = REPO_ROOT / "aixi"


mcp = FastMCP("aixi_tools")


def _run(cmd: List[str], cwd: Path | None = None, timeout: Optional[int] = None) -> tuple[int, str, str]:
    """Run a subprocess and capture stdout/stderr as text."""
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
        return 124, out, err + "\n[timeout expired]"
    return proc.returncode, out, err


def _tail(text: str, n: int = 80) -> str:
    lines = text.splitlines()
    if len(lines) <= n:
        return text
    return "\n".join(["… (truncated) …", *lines[-n:]])


@mcp.tool()
def list_envs() -> str:
    """List available environment config files under conf/.

    Returns:
        A newline-separated list of conf file basenames (e.g., tictactoe.conf).
    """
    if not CONF_DIR.exists():
        return "conf/ directory not found"
    confs = sorted(p.name for p in CONF_DIR.glob("*.conf"))
    if not confs:
        return "No .conf files found in conf/"
    return "\n".join(confs)


@mcp.tool()
def build(target: Optional[str] = None) -> str:
    """Run `make` at the repo root (optional target).

    Args:
        target: Optional make target (e.g., "clean", "test-agent").

    Returns:
        A concise summary of the build result with a tail of build logs.
    """
    cmd = ["make"] + ([target] if target else [])
    code, out, err = _run(cmd, cwd=REPO_ROOT)
    status = "success" if code == 0 else f"failed (exit {code})"
    tail = _tail((out or "") + ("\n" if out and err else "") + (err or ""), n=80)
    return f"make {' '.join(shlex.quote(x) for x in cmd[1:])} -> {status}\n\n{tail}"


@mcp.tool()
def run_agent(conf: str, log_path: Optional[str] = None) -> str:
    """Run the AIXI agent with a given config and log path.

    Args:
        conf: Path to conf file (relative to repo root or absolute). Example: "conf/tictactoe.conf".
        log_path: Optional log output path (default: auto under log/ with timestamp).

    Behavior:
        - Auto-builds the binary if missing by invoking `make`.
        - Runs `./aixi <conf> <log_path>` at repo root; returns a short run summary.
        - Honors optional timeout via env var `AIXI_TOOLS_RUN_TIMEOUT` (seconds).
          If unset, applies a conservative default for configs prefixed with
          `quick-` (30s); otherwise no timeout.
    """
    conf_path = Path(conf)
    if not conf_path.is_absolute():
        conf_path = REPO_ROOT / conf_path
    if not conf_path.exists():
        return f"Config not found: {conf_path}"

    if not AIXI_BIN.exists():
        _ = build(None)
        if not AIXI_BIN.exists():
            return "Build did not produce ./aixi"

    ts = time.strftime("%Y%m%d-%H%M%S")
    lp = Path(log_path) if log_path else (LOG_DIR / f"run-{conf_path.stem}-{ts}.log")
    lp.parent.mkdir(parents=True, exist_ok=True)

    # Resolve timeout policy
    timeout_env = os.getenv("AIXI_TOOLS_RUN_TIMEOUT")
    timeout_sec: Optional[int]
    if timeout_env:
        try:
            timeout_sec = int(timeout_env)
        except Exception:
            timeout_sec = None
    else:
        timeout_sec = 30 if conf_path.name.startswith("quick-") else None

    code, out, err = _run([str(AIXI_BIN), str(conf_path), str(lp)], cwd=REPO_ROOT, timeout=timeout_sec)
    status = "success" if code == 0 else f"failed (exit {code})"
    tail = _tail((out or "") + ("\n" if out and err else "") + (err or ""), n=60)
    note = f"Log written: {lp}"
    return f"aixi run -> {status}\n{note}\n\n{tail}"


@mcp.tool()
def graph_log(log_file: str) -> str:
    """Generate graphs from a log using graph.py.

    Args:
        log_file: Path to the .log (CSV-like) file to graph.

    Returns:
        Path to the output graph directory or an error message.
    """
    if not GRAPH_PY.exists():
        return f"graph.py not found at {GRAPH_PY}"
    log_path = Path(log_file)
    if not log_path.is_absolute():
        log_path = REPO_ROOT / log_path
    if not log_path.exists():
        return f"Log not found: {log_path}"

    code, out, err = _run([sys.executable, str(GRAPH_PY), str(log_path)], cwd=REPO_ROOT)
    status = "success" if code == 0 else f"failed (exit {code})"
    # graph.py writes to graph/<logfile>/. Return a best-effort path.
    out_dir = REPO_ROOT / "graph" / log_path.name
    msg = f"graph.py -> {status}\nOutput dir: {out_dir}"
    tail = _tail((out or "") + ("\n" if out and err else "") + (err or ""), n=40)
    return f"{msg}\n\n{tail}".strip()


@mcp.tool()
def summarize_log(log_file: str) -> str:
    """Summarize a CSV-like .log file produced by the agent.

    Args:
        log_file: Path to a log under log/ (e.g., "log/tictactoe.log").

    Returns:
        A human-readable summary including rows, final total reward, 
        final average reward, and mean reward per step.
    """
    p = Path(log_file)
    if not p.is_absolute():
        p = REPO_ROOT / p
    if not p.exists():
        return f"Log not found: {p}"

    with p.open("r", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        return f"Empty log: {p}"

    header = [h.strip() for h in rows[0]]
    data = rows[1:]
    if not data:
        return f"No data rows in log: {p}"

    # Build a quick name->index map (best-effort for common headers in this repo)
    name_to_idx = {name: i for i, name in enumerate(header)}
    def col_idx(name: str) -> Optional[int]:
        for key in name_to_idx:
            if key.lower() == name.lower():
                return name_to_idx[key]
        return None

    idx_reward = col_idx("reward")
    idx_total = col_idx("total reward")
    idx_avg = col_idx("average reward")

    n = len(data)
    # Compute metrics
    rewards: List[float] = []
    for r in data:
        try:
            if idx_reward is not None:
                rewards.append(float(r[idx_reward]))
        except Exception:
            pass

    mean_reward = sum(rewards) / len(rewards) if rewards else float("nan")

    last = data[-1]
    def safe_get(i: Optional[int]) -> str:
        if i is None:
            return "n/a"
        try:
            return str(last[i])
        except Exception:
            return "n/a"

    final_total = safe_get(idx_total)
    final_avg = safe_get(idx_avg)

    return (
        f"Summary for {p.name}:\n"
        f"- rows: {n}\n"
        f"- final total reward: {final_total}\n"
        f"- final average reward: {final_avg}\n"
        f"- mean reward per step: {mean_reward:.5f}"
    )


@mcp.tool()
def search_code(query: str, path: str = "src") -> str:
    """Search code for a string pattern (simple contains match).

    Args:
        query: Text to search for (case-insensitive substring).
        path: Directory to search (default: src).

    Returns:
        Up to 50 matches in the form `file:line: content`.
    """
    base = Path(path)
    if not base.is_absolute():
        base = REPO_ROOT / base
    if not base.exists():
        return f"Path not found: {base}"

    pattern = query.lower()
    matches: List[str] = []
    for p in base.rglob("*"):
        if p.is_dir():
            continue
        # Limit to plausible code/text files
        if p.suffix.lower() not in {".cpp", ".hpp", ".h", ".c", ".md", ".txt", ".conf", ".py", ".sh"}:
            continue
        try:
            with p.open("r", errors="ignore") as f:
                for i, line in enumerate(f, start=1):
                    if pattern in line.lower():
                        matches.append(f"{p.relative_to(REPO_ROOT)}:{i}: {line.rstrip()}")
                        if len(matches) >= 50:
                            raise StopIteration
        except StopIteration:
            break
        except Exception:
            continue

    if not matches:
        return f"No matches for {query!r} under {base.relative_to(REPO_ROOT)}"
    if len(matches) == 50:
        matches.insert(0, "… showing first 50 matches …")
    return "\n".join(matches)


if __name__ == "__main__":
    # Start the MCP server over stdio for local hosts (e.g., Claude Desktop).
    # Do not print to stdout; use stderr for any debug logs.
    mcp.run(transport="stdio")
