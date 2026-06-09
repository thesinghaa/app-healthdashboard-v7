"""
Agent 2 — Analyst
Model: ALT_MODEL (KEY2, separate TPM budget)
Job:   Deep analysis from a snippet of DC's briefing.
Context is passed as a string injected into the task description
(NOT via CrewAI context=[...]) so we avoid full execution-trace blowup.
"""

from crewai import Agent, Task
from .constants import ALT_MODEL, TONE_RULES


def make_agent() -> Agent:
    return Agent(
        role="Senior Public Health Programme Analyst",
        goal=(
            "Identify performance patterns, root causes, and actionable priorities "
            "for a senior health officer who must decide where to focus resources."
        ),
        backstory=(
            "Senior programme analyst, 12 years in public health monitoring across "
            "Northeast India. Arunachal Pradesh context: 27 districts, terrain "
            "challenges, sparse populations, limited monsoon transport."
        ),
        llm=ALT_MODEL,
        verbose=False,
        allow_delegation=False,
        max_iter=1,
        tools=[],
    )


def make_task(agent: Agent, division_id: str,
              div_full_name: str, dc_snippet: str) -> Task:
    return Task(
        description=(
            f"Produce a structured analytical assessment for {div_full_name} "
            f"division (NHM Arunachal Pradesh, FY 2025-26).\n\n"
            f"DATA BRIEFING FROM DATA COLLECTOR:\n{dc_snippet}\n\n"
            "REQUIRED SECTIONS (be concise — under 400 words total):\n"
            "1. TOP 3 CRITICAL PRIORITIES: programme, KD indicators with numbers, "
            "   2 contributing factors each.\n"
            "2. POSITIVE FINDINGS: 3 bright spots with exact numbers.\n"
            "3. STRATEGIC RECOMMENDATIONS: 6 items. Each: action | Responsible | Timeline.\n\n"
            f"{TONE_RULES}"
        ),
        expected_output=(
            "Concise structured analysis: Top 3 Critical Priorities, "
            "Positive Findings, 6 Strategic Recommendations. Under 400 words."
        ),
        agent=agent,
    )
