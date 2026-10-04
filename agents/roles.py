"""The four specialist agents: planner, researcher, writer, critic."""
from .llm import ask, ask_json, run_tool_loop


def plan(topic: str, past: list[dict]) -> list[str]:
    context = f"\nRelated past research (avoid repeating): {past}" if past else ""
    out = ask_json(
        "You are a research planner. Break a topic into 3-4 specific, non-overlapping "
        'sub-questions. Output: {"questions": ["...", "..."]}',
        f"Topic: {topic}{context}")
    return out["questions"][:4]


def research(question: str, schemas, functions, on_event=None) -> str:
    return run_tool_loop(
        "You are a researcher. Answer the question using web search and page reads. "
        "Use the calculator for any math. Return concise findings as bullet points, "
        "each with its source URL.",
        question, schemas, functions, max_steps=6, on_event=on_event)


def write(topic: str, findings: dict, previous: str = "", feedback: str = "") -> str:
    notes = "\n\n".join(f"### {q}\n{a}" for q, a in findings.items())
    revise = f"\n\nPrevious draft:\n{previous}\n\nCritic feedback to address:\n{feedback}" if feedback else ""
    return ask(
        "You are a technical writer. Write a clear markdown report with a summary, one "
        "section per sub-question, and a Sources list. Only use facts from the notes.",
        f"Topic: {topic}\n\nResearch notes:\n{notes}{revise}", max_tokens=4000)


def critique(topic: str, report: str) -> dict:
    return ask_json(
        "You are a strict reviewer. Check the report for unsupported claims, gaps, and "
        'missing sources. Output: {"approved": true/false, "feedback": "specific fixes"}',
        f"Topic: {topic}\n\nReport:\n{report}")
