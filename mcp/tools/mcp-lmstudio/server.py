from __future__ import annotations

from typing import Any, Optional, Union
import os
import json
import httpx
from mcp.server.fastmcp import FastMCP


"""
MCP server for LM Studio (local LLM API)

Exposes simple tools around LM Studio's OpenAI-compatible endpoints:
- GET /v1/models
- POST /v1/chat/completions (optionally with response_format for structured output)
- POST /v1/embeddings

Environment configuration:
- LMSTUDIO_BASE_URL (default: http://localhost:1234/v1)
- LMSTUDIO_API_KEY (default: "lm-studio")

Notes:
- Avoid stdout prints; use structured returns. FastMCP handles stdio transport.
- HTTP timeouts are conservative to keep the MCP host responsive.
"""


mcp = FastMCP("lmstudio")


def _base_url() -> str:
    return os.environ.get("LMSTUDIO_BASE_URL", "http://localhost:1234/v1").rstrip("/")


def _headers() -> dict[str, str]:
    api_key = os.environ.get("LMSTUDIO_API_KEY", "lm-studio").strip()
    # LM Studio examples often pass api_key="lm-studio"; include Authorization by default.
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}" if api_key else "",
    }


async def _http_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = f"{_base_url()}{path}"
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        resp = await client.post(url, headers=_headers(), json=payload)
        resp.raise_for_status()
        return resp.json()


async def _http_get(path: str) -> dict[str, Any]:
    url = f"{_base_url()}{path}"
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        resp = await client.get(url, headers=_headers())
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def lm_list_models() -> list[str]:
    """List currently loaded models from LM Studio (GET /v1/models)."""
    try:
        data = await _http_get("/models")
    except Exception as e:
        return [f"error: {type(e).__name__}: {e}"]
    models = data.get("data", [])
    ids: list[str] = []
    for m in models:
        mid = m.get("id")
        if isinstance(mid, str):
            ids.append(mid)
    return ids


@mcp.tool()
async def lm_chat(
    messages: list[dict[str, Any]],
    model: str,
    temperature: Optional[float] = 0.7,
    max_tokens: Optional[int] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    stop: Optional[list[str]] = None,
    presence_penalty: Optional[float] = None,
    frequency_penalty: Optional[float] = None,
    seed: Optional[int] = None,
    tools: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    """Call LM Studio chat completions (POST /v1/chat/completions).

    Args follow OpenAI's chat API shape. Returns the raw JSON response.
    """
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
    }
    # Optional parameters only if provided
    if temperature is not None:
        payload["temperature"] = temperature
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    if top_p is not None:
        payload["top_p"] = top_p
    if top_k is not None:
        payload["top_k"] = top_k
    if stop:
        payload["stop"] = stop
    if presence_penalty is not None:
        payload["presence_penalty"] = presence_penalty
    if frequency_penalty is not None:
        payload["frequency_penalty"] = frequency_penalty
    if seed is not None:
        payload["seed"] = seed
    if tools:
        payload["tools"] = tools

    try:
        data = await _http_post("/chat/completions", payload)
    except httpx.HTTPStatusError as he:
        return {"error": f"HTTP {he.response.status_code}", "details": he.response.text}
    except Exception as e:
        return {"error": f"{type(e).__name__}", "details": str(e)}
    return data


@mcp.tool()
async def lm_chat_structured(
    messages: list[dict[str, Any]],
    model: str,
    schema: dict[str, Any],
    temperature: Optional[float] = 0.7,
    max_tokens: Optional[int] = None,
) -> dict[str, Any]:
    """Call chat with Structured Output (response_format json_schema).

    Returns a dict with fields:
    - raw: full LM Studio response
    - parsed: parsed JSON object from choices[0].message.content (if parseable)
    - content: original string content
    """
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": schema.get("name", "result"),
            # LM Studio examples sometimes include strict: "true"
            # Keep user-provided schema as-is under "schema" key.
            "schema": schema.get("schema", schema),
        },
    }
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "response_format": response_format,
    }
    if temperature is not None:
        payload["temperature"] = temperature
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens

    try:
        raw = await _http_post("/chat/completions", payload)
    except httpx.HTTPStatusError as he:
        return {"error": f"HTTP {he.response.status_code}", "details": he.response.text}
    except Exception as e:
        return {"error": f"{type(e).__name__}", "details": str(e)}

    content: Optional[str] = None
    try:
        ch = raw.get("choices", [])[0]
        msg = ch.get("message", {}) if isinstance(ch, dict) else {}
        content = msg.get("content")
    except Exception:
        content = None

    parsed: Any = None
    if isinstance(content, str):
        try:
            parsed = json.loads(content)
        except Exception:
            parsed = None

    return {"raw": raw, "content": content, "parsed": parsed}


@mcp.tool()
async def lm_embeddings(
    text: Union[str, list[str]],
    model: str,
) -> dict[str, Any]:
    """Get embeddings from LM Studio (POST /v1/embeddings). Returns raw JSON."""
    payload: dict[str, Any] = {
        "model": model,
        "input": text if isinstance(text, list) else [text],
    }
    try:
        data = await _http_post("/embeddings", payload)
    except httpx.HTTPStatusError as he:
        return {"error": f"HTTP {he.response.status_code}", "details": he.response.text}
    except Exception as e:
        return {"error": f"{type(e).__name__}", "details": str(e)}
    return data


if __name__ == "__main__":
    # Run the MCP server using stdio transport.
    mcp.run(transport="stdio")

