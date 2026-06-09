"""
CrewAI orchestrator — builds and runs the 4-agent pipeline.

Agent scripts live in agents/:
  data_collector.py  → Agent 1 + Task 1
  analyst.py         → Agent 2 + Task 2
  report_writer.py   → Agent 3 + Task 3
  quality_checker.py → Agent 4 + Task 4

Agents now fetch their own data via @tool-decorated tool wrappers.
"""

import time
import threading
from crewai import Crew, Process

from agents import (
    collector_agent, collector_task,
    analyst_agent,   analyst_task,
    writer_agent,    writer_task,
    checker_agent,   checker_task,
)

# 30-second gap between tasks.
# KEY1 agents (DC, Writer) and KEY2 agents (Analyst, QC) each have 6000 TPM/min.
# Alternating keys means no shared window — 30s gap is a safety buffer.
PACE_SECONDS = 30


def build_crew(division_id: str, div_full_name: str,
               step_callback=None) -> Crew:
    """
    Returns a configured Crew ready to kickoff().
    step_callback(step_idx: int) is called after each task completes (0-based).
    Agents fetch KD/HMIS/chart data themselves via their assigned tools.
    """
    # Instantiate agents
    c = collector_agent()
    a = analyst_agent()
    w = writer_agent()
    q = checker_agent()

    # Build tasks — agents receive division_id and call tools themselves
    t1 = collector_task(c, division_id, div_full_name)
    t2 = analyst_task(a, division_id, div_full_name, context=[t1])
    t3 = writer_task(w, division_id, div_full_name, context=[t1, t2])
    t4 = checker_task(q, division_id, context=[t1, t3])

    # Step callbacks + pacing
    _step = [0]
    _lock = threading.Lock()

    def _on_task_end(task_output):
        with _lock:
            _step[0] += 1
            if step_callback:
                step_callback(_step[0])
            # Pace: sleep before next LLM call (not after last task)
            if _step[0] < 3:
                time.sleep(PACE_SECONDS)

    t1.callback = _on_task_end
    t2.callback = _on_task_end
    t3.callback = _on_task_end

    return Crew(
        agents=[c, a, w, q],
        tasks=[t1, t2, t3, t4],
        process=Process.sequential,
        verbose=False,
    )


def run_report(division_id: str, div_full_name: str,
               step_callback=None) -> str:
    crew = build_crew(division_id, div_full_name, step_callback)
    result = crew.kickoff()
    return str(result)
