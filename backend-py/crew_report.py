"""
CrewAI orchestrator — runs 4 agents sequentially with strict context control.

Each agent is a separate single-agent Crew. Output is truncated before
passing to the next agent so we stay under Groq free-tier 6000 TPM/minute.

Agent token budget (input tokens per LLM call, free-tier limit = 6000):
  DC      : ~2500 (own prompt + tool results)
  Analyst : ~2500 (own prompt + truncated DC output 1200 chars)
  Writer  : ~3500 (own prompt + truncated briefing 2000 chars + chart tool result)
  QC      : ~3000 (own prompt + truncated Writer HTML 1500 chars)
"""

import time, threading
from crewai import Crew, Process

from agents import (
    collector_agent, collector_task,
    analyst_agent,   analyst_task,
    writer_agent,    writer_task,
    checker_agent,   checker_task,
)

# Gap between agent runs — gives TPM window time to clear on same key
PACE_SECONDS = 20

# Max chars of each agent's output to pass as context to the next agent
# (~4 chars per token → 1200 chars ≈ 300 tokens context injection)
DC_TRUNCATE      = 1200
ANALYST_TRUNCATE = 1200
WRITER_TRUNCATE  = 2000   # writer output is HTML — QC needs more of it


def _run_single(agent, task, max_retries: int = 4) -> str:
    """Run one agent in isolation — no shared CrewAI context.
    Retries up to max_retries times on Groq rate-limit errors,
    waiting 5/10/20/30 seconds between attempts to outlast the TPM window."""
    import litellm as _litellm
    wait_schedule = [5, 10, 20, 30]
    for attempt in range(max_retries):
        try:
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=False,
            )
            result = crew.kickoff()
            return str(result).strip()
        except _litellm.RateLimitError:
            if attempt >= max_retries - 1:
                raise
            wait = wait_schedule[min(attempt, len(wait_schedule) - 1)]
            time.sleep(wait)


def run_report(division_id: str, div_full_name: str,
               step_callback=None) -> str:
    """
    Run 4 agents sequentially with controlled context. Returns final HTML.
    step_callback(idx) fires after each agent completes.
    """

    # ── Agent 1: DataCollector ─────────────────────────────────────────
    c   = collector_agent()
    t1  = collector_task(c, division_id, div_full_name)
    dc_output = _run_single(c, t1)
    if step_callback:
        step_callback(1)
    time.sleep(PACE_SECONDS)

    # Truncate DC output before passing as context injection
    dc_snippet = dc_output[:DC_TRUNCATE]

    # ── Agent 2: Analyst ───────────────────────────────────────────────
    a  = analyst_agent()
    t2 = analyst_task(a, division_id, div_full_name, dc_snippet)
    an_output = _run_single(a, t2)
    if step_callback:
        step_callback(2)
    time.sleep(PACE_SECONDS)

    analyst_snippet = an_output[:ANALYST_TRUNCATE]

    # ── Agent 3: ReportWriter ──────────────────────────────────────────
    w  = writer_agent()
    t3 = writer_task(w, division_id, div_full_name,
                     dc_snippet, analyst_snippet)
    html_raw = _run_single(w, t3)
    if step_callback:
        step_callback(3)
    time.sleep(PACE_SECONDS)

    writer_snippet = html_raw[:WRITER_TRUNCATE]

    # ── Agent 4: QualityChecker ────────────────────────────────────────
    q  = checker_agent()
    t4 = checker_task(q, division_id, writer_snippet)
    final_html = _run_single(q, t4)
    if step_callback:
        step_callback(4)

    return final_html
