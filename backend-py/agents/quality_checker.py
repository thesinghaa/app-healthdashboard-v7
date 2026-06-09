"""
Agent 4 — QualityChecker
Model: strong (llama-3.3-70b-versatile)
Job:   Fix banned words, em-dashes, missing data references. Output corrected HTML only.
"""

from crewai import Agent, Task
from .constants import STRONG_MODEL
from tools.agent_tools import kd_summary_tool


def make_agent() -> Agent:
    return Agent(
        role="Editorial Quality Reviewer",
        goal=(
            "Ensure the HTML report meets PIF tone standards, contains no prohibited "
            "language, and that every factual claim is backed by data from the briefing."
        ),
        backstory=(
            "You are the editorial lead at Pahlé India Foundation. You review every "
            "report before it goes to government officers. You catch: (1) prohibited "
            "negative words — failing, failure, struggling, poor, weak, inadequate, "
            "alarming; (2) em-dashes or en-dashes anywhere in the text; (3) "
            "recommendations without a responsible party or timeline; (4) claims "
            "that cite no specific numbers. You output the corrected final HTML "
            "and nothing else."
        ),
        llm=STRONG_MODEL,
        verbose=False,
        allow_delegation=False,
        max_iter=2,
        tools=[kd_summary_tool],
    )


def make_task(agent: Agent, division_id: str, context: list) -> Task:
    return Task(
        description=(
            "Review the HTML report produced by the ReportWriter and fix any issues.\n\n"
            f"If any factual claim looks uncertain, call the 'KD Summary' tool "
            f"with division_id='{division_id}' to verify the number against source data.\n\n"
            "CHECK FOR AND FIX:\n"
            "1. Prohibited words: failing, failure, is failing, struggling, "
            "   poor performance, inadequate, weak, disappointing, alarming. "
            "   Replace with: 'has scope for improvement', 'requires focused attention', "
            "   'presents an opportunity to accelerate'.\n"
            "2. Em-dashes (—) or en-dashes (–): replace every one with a comma "
            "   or full stop.\n"
            "3. Recommendations missing a responsible party or timeline: add them.\n"
            "4. Any claim with no number or indicator name: add the data reference.\n"
            "5. Ensure all 8 report sections are present and complete.\n\n"
            "OUTPUT: the complete corrected HTML document and nothing else. "
            "Do not add any commentary, explanation, or markdown around the HTML."
        ),
        expected_output=(
            "The corrected, final HTML document starting with <!DOCTYPE html>. "
            "No additional text. No markdown fences."
        ),
        agent=agent,
        context=context,
    )
