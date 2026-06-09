"""
Agent 4 — QualityChecker
Model: strong (llama-3.3-70b-versatile)
Job:   Fix banned words, em-dashes, missing data references. Output corrected HTML only.
"""

from crewai import Agent, Task
from .constants import ALT_MODEL
def make_agent() -> Agent:
    return Agent(
        role="Editorial Quality Reviewer",
        goal=(
            "Ensure the HTML report meets PIF tone standards, contains no prohibited "
            "language, and every recommendation has a responsible party and timeline."
        ),
        backstory=(
            "You are the editorial lead at Pahlé India Foundation. You catch: "
            "(1) prohibited negative words; (2) em-dashes or en-dashes; "
            "(3) recommendations missing responsible party or timeline; "
            "(4) claims with no number or indicator name. "
            "You output the corrected final HTML and nothing else."
        ),
        llm=ALT_MODEL,
        verbose=False,
        allow_delegation=False,
        max_iter=1,
        tools=[],
    )


def make_task(agent: Agent, division_id: str, context: list) -> Task:
    return Task(
        description=(
            "Review the HTML report in context and fix ALL issues in one pass.\n\n"
            "FIX:\n"
            "1. Prohibited words: failing/failure/struggling/poor performance/"
            "inadequate/weak/disappointing/alarming. "
            "Replace with: 'has scope for improvement' or 'requires focused attention'.\n"
            "2. Em-dashes (--) or en-dashes: replace with comma or full stop.\n"
            "3. Recommendations missing responsible party or timeline: add them.\n"
            "4. Claims with no number or indicator: add the data reference.\n\n"
            "OUTPUT: complete corrected HTML starting with <!DOCTYPE html>. "
            "No commentary. No markdown."
        ),
        expected_output=(
            "The corrected final HTML document starting with <!DOCTYPE html>. "
            "No additional text. No markdown fences."
        ),
        agent=agent,
        context=context,
    )
