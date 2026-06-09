"""
Agent 2 — Analyst
Model: strong (llama-3.3-70b-versatile)
Job:   Deep analysis — root causes, priorities, 6 strategic recommendations.
"""

from crewai import Agent, Task
from .constants import ALT_MODEL, TONE_RULES
from tools.agent_tools import kd_raw_tool


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
            "how to translate data into strategic priorities. Arunachal Pradesh "
            "context you always keep in mind: 27 districts, significant terrain "
            "challenges, sparse populations in remote areas, limited transport "
            "during monsoon, and ongoing capacity-building needs at block level. "
            "You frame challenges constructively, as opportunities for improvement."
        ),
        llm=ALT_MODEL,
        verbose=False,
        allow_delegation=False,
        max_iter=2,
        tools=[kd_raw_tool],
    )


def make_task(agent: Agent, division_id: str, div_full_name: str, context: list) -> Task:
    return Task(
        description=(
            f"Using the data briefing and your 'KD Raw Data' tool, produce a deep "
            f"analytical assessment for {div_full_name} division (division_id='{division_id}').\n\n"
            "If you need to verify specific indicator numbers, call the 'KD Raw Data' tool "
            f"with division_id='{division_id}' to access the full indicator tree.\n\n"
            "REQUIRED SECTIONS:\n"
            "1. TOP 3 CRITICAL PRIORITIES: for each — programme name, the specific "
            "   KD indicators of concern with exact numbers, and 2 to 3 likely "
            "   contributing factors drawn from: supply chain, HR availability, "
            "   training needs, geographic access, community awareness, "
            "   infrastructure gaps, seasonal constraints.\n"
            "2. POSITIVE FINDINGS: 3 genuine bright spots with specific numbers. "
            "   Explain why each achievement is significant for beneficiary health.\n"
            "3. SYSTEMIC PATTERNS: cross-programme issues affecting multiple "
            "   programmes (e.g., last-mile supply chain, frontline worker gaps, "
            "   digital reporting lags).\n"
            "4. STRATEGIC RECOMMENDATIONS: 6 specific, actionable recommendations. "
            "   Each must have: the action, responsible party (e.g., District CMO, "
            "   Block PHC, State NHM), and a realistic timeline (weeks or months).\n\n"
            f"{TONE_RULES}\n"
            "Write in clear, officer-facing language. Be specific, not generic."
        ),
        expected_output=(
            "A structured analysis with: Top 3 Critical Priorities (with contributing "
            "factors), Positive Findings, Systemic Patterns, Strategic Recommendations "
            "(6 items, each with responsible party and timeline)."
        ),
        agent=agent,
        context=context,
    )
