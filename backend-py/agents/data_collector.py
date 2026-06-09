"""
Agent 1 — DataCollector
Model: fast (llama-3.1-8b-instant)
Job:   Call KD Summary + HMIS Trends tools, produce a structured performance briefing.
"""

from crewai import Agent, Task
from .constants import FAST_MODEL
from tools.agent_tools import kd_summary_tool, hmis_trends_tool


def make_agent() -> Agent:
    return Agent(
        role="NHM Data Aggregator",
        goal=(
            "Compile a concise, structured performance briefing for the division "
            "so analysts can immediately understand the current programme situation."
        ),
        backstory=(
            "You are a data analyst at Pahlé India Foundation (PIF), embedded "
            "with the NHM Arunachal Pradesh team. You excel at reading HMIS data, "
            "interpreting KD achievement ratios, and flagging issues with precision. "
            "You present facts neutrally, always citing exact indicator codes and numbers."
        ),
        llm=FAST_MODEL,
        verbose=False,
        allow_delegation=False,
        max_iter=2,
        tools=[kd_summary_tool, hmis_trends_tool],
    )


def make_task(agent: Agent, division_id: str, div_full_name: str) -> Task:
    return Task(
        description=(
            f"Collect and structure all performance data for the {div_full_name} "
            f"division (division_id='{division_id}'), NHM Arunachal Pradesh FY 2025-26.\n\n"
            "STEP 1: Call the 'KD Summary' tool with division_id to get the KD performance summary.\n"
            "STEP 2: Call the 'HMIS Trends' tool with division_id to get live monthly HMIS data.\n\n"
            "Produce a structured data briefing with ALL of the following sections:\n"
            "1. DIVISION SNAPSHOT: total programmes, KD counts by status "
            "(achieved / caution / gap), overall achievement rate.\n"
            "2. PROGRAMME TABLE: for each programme — name, status "
            "(On Track / Caution / Critical), KDs achieved/caution/gap, "
            "the single most important metric.\n"
            "3. TOP 5 CRITICAL GAPS: indicator name, current value, target, "
            "percentage gap. Sort by largest gap first.\n"
            "4. TOP 3 ACHIEVEMENTS: indicator name, value, target, "
            "why it matters.\n"
            "5. HMIS TREND OBSERVATIONS: monthly data patterns, improving or "
            "declining indicators, seasonality.\n"
            "Be precise with numbers. Do not add commentary or recommendations yet."
        ),
        expected_output=(
            "A structured text briefing with sections: Division Snapshot, "
            "Programme Table, Top 5 Critical Gaps, Top 3 Achievements, "
            "HMIS Trend Observations."
        ),
        agent=agent,
    )
