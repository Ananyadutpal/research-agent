"""Thin wrapper around the Anthropic API: plain calls, JSON calls, and the tool-use loop."""
import json
import os

import anthropic

MODEL = os.getenv("AGENT_MODEL", "claude-sonnet-5-5")
_client = None


def client() -> anthropic.Anthropic:
    global _client
    if _client is None:  # lazy so tests can import without an API key
        _client = anthropic.Anthropic()
    return _client


def ask(system: str, prompt: str, max_tokens: int = 3000) -> str:
    r = client().messages.create(
        model=MODEL, max_tokens=max_tokens, system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in r.content if b.type == "text")


def parse_json(text: str):
    """Extract the first JSON object/array from model output (handles ```json fences)."""
    starts = [i for i in (text.find("{"), text.find("[")) if i != -1]
    if not starts:
        raise ValueError(f"No JSON found in: {text[:100]}")
    start = min(starts)
    end = max(text.rfind("}"), text.rfind("]")) + 1
    return json.loads(text[start:end])


def ask_json(system: str, prompt: str):
    return parse_json(ask(system + "\nRespond with ONLY valid JSON.", prompt))


def run_tool_loop(system, prompt, schemas, functions, max_steps=8, on_event=None):
    """Generic agent loop: model picks a tool -> we run it -> feed result back -> repeat."""
    emit = on_event or (lambda *_: None)
    messages = [{"role": "user", "content": prompt}]
    for step in range(1, max_steps + 1):
        resp = client().messages.create(
            model=MODEL, max_tokens=3000, system=system, tools=schemas, messages=messages
        )
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")

        results = []
        for block in resp.content:
            if block.type != "tool_use":
                continue
            emit("tool", f"{block.name}({json.dumps(block.input)[:90]})")
            try:
                out = functions[block.name](**block.input)
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(out)})
            except Exception as e:  # let the agent see the error and adapt
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": f"Error: {e}", "is_error": True})
        messages.append({"role": "user", "content": results})
    return "Stopped: max steps reached."
