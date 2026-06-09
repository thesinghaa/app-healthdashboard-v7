"""
Agent 2 — Analyst
Model: ALT_MODEL (KEY2, separate TPM budget)
Job:   Deep analysis from DC briefing — root causes, priorities, 6 strategic recommendations.
No tools — DC briefing already contains all needed data. Calling kd_raw_tool
would dump ~10k-token JSON, blowing the 6000 TPM limit.
"""

from crewai import Agent, Task
from .constants import ALT_MODEL, TONE_RULES


def make_agent() -> Agent:
    return Agent(
        role="Senior Public Health Programme Analyst",
        goal=(
            "Identify the most important performance patterns, root causes, and "
            "actionable priorities for the division, framed for a senior health "
            "officer who must decide where to focus resources next quarter."
        ),
        backstory=(
            "You are a senior programme analyst with 12 years of experience in "
            "public health monitoring across Northeast India. You understand NHM "
            "structures, district-level constraints in remote tribal states, and "
            "how to translate data into strategic priorities. Arunachal Pradesh: "
            "27 districts, terrain challenges, sparse populations, limited transport "
            "in monsoon, ongoing capacity-building needs at block level."
        ),
        llm=ALT_MODEL,
        verbose=False,
        allow_delegation=False,
        max_iter=1,
        tools=[],
    )


def make_task(agent: Agent, division_id: str, div_full_name: str, context: list) -> Task:
    return Task(
        description=(
            f"Using ONLY the data briefing provided in context, produce a deep "
            f"analytical assessment for {div_full_name} division.\n\n"
            "REQUIRED SECTIONS:\n"
            "1. TOP 3 CRITICAL PRIORITIES: programme name, specific KD indicators "
            "   with exact numbers, 2-3 contributing factors (supply chain, HR, "
            "   training, geographic access, community awareness).\n"
            "2. POSITIVE FINDINGS: 3 bright spots with specific numbers and why "
            "   each matters for beneficiary health.\n"
            "3. SYSTEMIC PATTERNS: cross-programme issues (supply chain, HR gaps, "
            "   digital reporting lags).\n"
            "4. STRATEGIC RECOMMENDATIONS: 6 specific, actionable items. "
            "   Each: action | Responsible party | Timeline.\n\n"
            f"{TONE_RULES}"
        ),
        expected_output=(
            "Structured analysis: Top 3 Critical Priorities, Positive Findings, "
            "Systemic Patterns, 6 Strategic Recommendations with responsible party "
            "and timeline for each."
        ),
        agent=agent,
        context=context,
    )
