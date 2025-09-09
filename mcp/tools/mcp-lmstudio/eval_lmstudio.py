#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx


def env(key: str, default: Optional[str] = None) -> Optional[str]:
    v = os.environ.get(key)
    return v if v is not None else default


def default_base_url() -> str:
    # LM Studio default OpenAI-compatible base
    return env("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")


def default_api_key() -> str:
    # LM Studio often accepts any non-empty token
    return env("LMSTUDIO_API_KEY", "lm-studio")


def now_iso() -> str:
    import datetime as _dt

    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def join_content(message_content: Any) -> str:
    # Handle both string content and array-of-parts content
    if isinstance(message_content, str):
        return message_content
    if isinstance(message_content, list):
        parts = []
        for item in message_content:
            if isinstance(item, dict):
                if "text" in item:
                    parts.append(str(item["text"]))
                elif "type" in item and item["type"] == "output_text" and "text" in item:
                    parts.append(str(item["text"]))
        return "".join(parts)
    return str(message_content)


def extract_first_number(text: str) -> Optional[float]:
    m = re.search(r"[-+]?(?:\d+\.\d+|\d+)", text)
    if not m:
        return None
    try:
        return float(m.group(0))
    except Exception:
        return None


def parse_json_from_text(text: str) -> Optional[Any]:
    # Try simple parse; else extract between first { and last }
    try:
        return json.loads(text)
    except Exception:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = text[start : end + 1]
        try:
            return json.loads(snippet)
        except Exception:
            return None
    return None


def validate_basic_schema(obj: Any, schema: Dict[str, Any]) -> Tuple[bool, str]:
    # Minimal validator to avoid external deps
    if schema.get("type") == "object":
        if not isinstance(obj, dict):
            return False, "not an object"
        props = schema.get("properties", {})
        required = schema.get("required", [])
        for key in required:
            if key not in obj:
                return False, f"missing required: {key}"
        # type checks
        for key, rules in props.items():
            if key in obj and "type" in rules:
                t = rules["type"]
                val = obj[key]
                if t == "string" and not isinstance(val, str):
                    return False, f"{key} not string"
                if t == "integer" and not (isinstance(val, int) and not isinstance(val, bool)):
                    return False, f"{key} not integer"
                if t == "number" and not (isinstance(val, (int, float)) and not isinstance(val, bool)):
                    return False, f"{key} not number"
                if t == "array" and not isinstance(val, list):
                    return False, f"{key} not array"
        return True, "ok"
    return True, "schema not enforced"


def http_post_json(base_url: str, api_key: str, path: str, payload: Dict[str, Any]) -> httpx.Response:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    url = base_url.rstrip("/") + path
    with httpx.Client(timeout=60) as client:
        return client.post(url, headers=headers, json=payload)


def http_get_json(base_url: str, api_key: str, path: str) -> httpx.Response:
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    url = base_url.rstrip("/") + path
    with httpx.Client(timeout=30) as client:
        return client.get(url, headers=headers)


def list_models(base_url: str, api_key: str) -> List[str]:
    try:
        r = http_get_json(base_url, api_key, "/models")
        r.raise_for_status()
        data = r.json()
        models = []
        for m in data.get("data", []):
            mid = m.get("id") or m.get("name")
            if mid:
                models.append(mid)
        return models
    except Exception:
        return []


def pick_default_model(base_url: str, api_key: str) -> Optional[str]:
    models = list_models(base_url, api_key)
    preferred = [
        "openai/gpt-oss-20b",
        "nousresearch/hermes-2-pro",
        "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "qwen/Qwen2.5-7B-Instruct",
    ]
    for p in preferred:
        if p in models:
            return p
    return models[0] if models else None


def chat_once(
    base_url: str,
    api_key: str,
    model: str,
    messages: List[Dict[str, Any]],
    *,
    tools: Optional[List[Dict[str, Any]]] = None,
    response_format: Optional[Dict[str, Any]] = None,
    temperature: float = 0.2,
    max_tokens: Optional[int] = 512,
) -> Tuple[Dict[str, Any], str, Optional[List[Dict[str, Any]]]]:
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    if tools:
        payload["tools"] = tools
    if response_format:
        payload["response_format"] = response_format

    t0 = time.perf_counter()
    r = http_post_json(base_url, api_key, "/chat/completions", payload)
    latency = time.perf_counter() - t0
    r.raise_for_status()
    data = r.json()
    # parse content
    content_str = ""
    tool_calls = None
    try:
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        tool_calls = message.get("tool_calls")
        content_str = join_content(message.get("content", ""))
    except Exception:
        content_str = json.dumps(data)[:2000]
    # attach measured latency for logging
    data["_latency_s"] = latency
    return data, content_str, tool_calls


def evaluate_task(
    base_url: str,
    api_key: str,
    model: str,
    task: Dict[str, Any],
    temperature: float,
    max_tokens: Optional[int],
) -> Dict[str, Any]:
    task_id = task["id"]
    task_type = task["type"]
    prompt = task["prompt"]
    system = task.get("system")
    messages: List[Dict[str, Any]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response_format: Optional[Dict[str, Any]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    if task_type == "json":
        if task.get("use_json_schema"):
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": task_id,
                    "schema": task["schema"],
                },
            }
        else:
            response_format = {"type": "json_object"}
        # Encourage compliance even if model ignores response_format
        messages.insert(0, {
            "role": "system",
            "content": "You must output only strict JSON matching the required schema.",
        })

    if task_type == "tool_use":
        tools = task.get("tools")
        messages.insert(0, {
            "role": "system",
            "content": "You can call tools when helpful. If tool calls are not supported, produce a reasonable final answer anyway.",
        })

    ok = False
    score = 0.0
    error: Optional[str] = None
    content = ""
    usage = None
    latency = None
    tool_calls = None
    raw: Dict[str, Any] = {}
    try:
        raw, content, tool_calls = chat_once(
            base_url,
            api_key,
            model,
            messages,
            tools=tools,
            response_format=response_format,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        latency = raw.get("_latency_s")
        usage = raw.get("usage")
        # Scoring
        if task_type == "regex":
            pattern = task["expected_regex"]
            flags = re.I if task.get("case_insensitive") else 0
            ok = re.search(pattern, content, flags) is not None
        elif task_type == "numeric":
            expected = float(task["expected_number"])
            val = extract_first_number(content)
            ok = val is not None and abs(val - expected) < 1e-6
        elif task_type == "json":
            obj = parse_json_from_text(content)
            if obj is None:
                ok = False
                error = "failed_to_parse_json"
            else:
                ok_schema, reason = validate_basic_schema(obj, task["schema"])
                ok = ok_schema
                if not ok_schema:
                    error = reason
        elif task_type == "tool_use":
            # Consider success if tool_calls are present or the content looks like a greeting with a time
            has_tools = bool(tool_calls)
            looks_good = bool(re.search(r"\bSam\b", content)) and bool(re.search(r"\b\d{2}:\d{2}", content))
            ok = has_tools or looks_good
        else:
            ok = True if content else False
        score = 1.0 if ok else 0.0
    except httpx.ConnectError:
        error = "connect_error: is LM Studio running and a model loaded?"
    except Exception as e:
        error = f"exception: {e}"

    return {
        "id": task_id,
        "category": task.get("category"),
        "type": task_type,
        "prompt": prompt,
        "success": bool(ok),
        "score": score,
        "latency_s": latency,
        "usage": usage,
        "content": content,
        "tool_calls": tool_calls,
        "error": error,
        "model": model,
        "ts": now_iso(),
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Evaluate a local LM Studio model on simple tasks.")
    ap.add_argument("--base-url", default=default_base_url(), help="OpenAI-compatible base URL (default: LM Studio http://localhost:1234/v1)")
    ap.add_argument("--api-key", default=default_api_key(), help="API key (LM Studio accepts any non-empty token)")
    ap.add_argument("--model", default=None, help="Model ID to use (defaults to a preferred available model)")
    ap.add_argument("--tasks", default=str(Path(__file__).with_name("eval_tasks.json")), help="Path to tasks JSON file")
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--output-dir", default=str(Path(__file__).resolve().parents[2] / "log"))
    args = ap.parse_args(argv)

    base_url = args.base_url
    api_key = args.api_key
    model = args.model or pick_default_model(base_url, api_key)
    if not model:
        print("No model specified and none found. Please pass --model or load a model in LM Studio.", file=sys.stderr)
        return 2

    tasks_path = Path(args.tasks)
    tasks_spec = read_json(tasks_path)
    tasks = tasks_spec.get("tasks", [])
    out_dir = Path(args.output_dir)
    ensure_dir(out_dir)
    run_id = f"llm_eval-{int(time.time())}"
    out_jsonl = out_dir / f"{run_id}.jsonl"

    print(f"Evaluating model: {model}")
    print(f"Base URL: {base_url}")
    print(f"Tasks: {tasks_path}")
    print(f"Writing results: {out_jsonl}")

    results: List[Dict[str, Any]] = []
    ok_count = 0
    t_start = time.perf_counter()
    with out_jsonl.open("w", encoding="utf-8") as f:
        for t in tasks:
            res = evaluate_task(
                base_url,
                api_key,
                model,
                t,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
            )
            results.append(res)
            if res.get("success"):
                ok_count += 1
            f.write(json.dumps(res, ensure_ascii=False) + "\n")
            print(f"- {t['id']}: {'PASS' if res.get('success') else 'FAIL'} ({res.get('latency_s'):.2f}s)")

    total = len(results)
    elapsed = time.perf_counter() - t_start
    overall = ok_count / total if total else 0.0
    # Per-category summary
    cats: Dict[str, Tuple[int, int]] = {}
    for r in results:
        c = r.get("category", "uncategorized")
        s = 1 if r.get("success") else 0
        if c not in cats:
            cats[c] = (0, 0)
        p, n = cats[c]
        cats[c] = (p + s, n + 1)

    print("\nSummary")
    print(f"- Total: {ok_count}/{total} passed; score={overall:.2%}")
    for c, (p, n) in sorted(cats.items()):
        print(f"- {c}: {p}/{n} passed; {p/n:.0%}")
    print(f"- Elapsed: {elapsed:.2f}s")
    print(f"- Results JSONL: {out_jsonl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

