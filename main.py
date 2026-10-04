"""Multi-agent research pipeline: plan -> research (parallel) -> write -> critique loop -> save.

Usage: python main.py "impact of solid-state batteries on EVs"
"""
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from agents import roles
from agents.memory import Memory
from agents.tools import build_tools

MAX_REVISIONS = 2


def run(topic: str, on_event=print, memory: Memory | None = None) -> tuple[str, str]:
    """Run the full pipeline. Returns (report_markdown, saved_path)."""
    memory = memory or Memory()
    os.makedirs("traces", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    trace = []

    def emit(kind, msg):
        trace.append({"t": round(time.time(), 2), "kind": kind, "msg": msg})
        on_event(f"[{kind}] {msg}")

    # 1. Plan (aware of past research via memory)
    past = memory.search(topic)
    questions = roles.plan(topic, past)
    emit("plan", " | ".join(questions))

    # 2. Research each sub-question in parallel
    schemas, functions = build_tools(memory)

    def work(q):
        return q, roles.research(q, schemas, functions, on_event=emit)

    with ThreadPoolExecutor(max_workers=len(questions)) as pool:
        findings = dict(pool.map(work, questions))
    emit("research", f"completed {len(findings)} sub-questions")

    # 3. Write, then let the critic send it back for revision
    report = roles.write(topic, findings)
    for i in range(MAX_REVISIONS):
        review = roles.critique(topic, report)
        emit("critic", f"round {i + 1}: approved={review['approved']}")
        if review["approved"]:
            break
        report = roles.write(topic, findings, previous=report, feedback=review["feedback"])

    # 4. Persist report, memory, and the execution trace
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:50]
    path = f"reports/{slug}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    memory.save(topic, report)
    with open(f"traces/{slug}-{datetime.now():%H%M%S}.jsonl", "w") as f:
        f.writelines(json.dumps(e) + "\n" for e in trace)
    emit("done", f"saved {path}")
    return report, path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Usage: python main.py "your research topic"')
    run(" ".join(sys.argv[1:]))
