# Multi-Agent Research Assistant

A team of specialised AI agents that plans, researches, writes and peer-reviews a cited report on any topic.

## Architecture

```
            ┌──────────┐   sub-questions   ┌─────────────────────────┐
 topic ───▶ │ Planner  │ ────────────────▶ │ Researchers (parallel)  │
            └────▲─────┘                   │ tools: search, fetch,   │
                 │ past research           │ calculator, memory      │
            ┌────┴─────┐                   └───────────┬─────────────┘
            │  Memory  │◀── saves report ──┐           │ findings
            │ (SQLite) │                   │     ┌─────▼─────┐   feedback   ┌────────┐
            └──────────┘                   └──── │  Writer   │ ◀─────────── │ Critic │
                                                 └─────┬─────┘ ───draft───▶ └────────┘
                                                       ▼
                                              reports/*.md + traces/*.jsonl
```

| Agent | Job |
|---|---|
| Planner | Splits the topic into sub-questions, avoiding what memory already covers |
| Researcher | Tool-use loop per sub-question; runs in parallel threads |
| Writer | Drafts a markdown report from findings only |
| Critic | Reviews for unsupported claims; triggers up to 2 revisions |

## Engineering details
- Framework-free agent loop with step caps and error feedback (`is_error`) so agents self-recover
- Safe calculator tool using AST parsing instead of `eval()`
- Persistent memory in SQLite, exposed both to the planner and as an agent tool
- Parallel research with `ThreadPoolExecutor`
- JSONL execution traces for debugging and observability
- Unit tests for tools, JSON parsing and memory (no API key needed)

## Run

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key
python main.py "impact of solid-state batteries on EVs"   # CLI
streamlit run app.py                                      # UI
pytest                                                    # tests
```

## Resume bullets
- Built a multi-agent research system (planner, parallel researchers, writer, critic) in Python on the Anthropic API, producing cited reports with an automated review-and-revise loop.
- Implemented tool use (web search, page fetch, sandboxed AST calculator), SQLite long-term memory, and JSONL tracing; cut research latency by running sub-questions concurrently.
- Added unit tests, a Streamlit UI, and reliability controls (step limits, error recovery, context truncation).
