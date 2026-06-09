"""
Agent 4 — QualityChecker
Model: ALT_MODEL (KEY2, new window after 20s pace)
Job:   Fix banned words, em-dashes, missing data refs. Output corrected HTML only.
Context = truncated Writer HTML injected into task description.
"""

from crewai import Agent, Task
from .constants import ALT_MODEL


def make_agent() -> Agent:
    return Agent(
        role="Editorial Quality Reviewer",
        goal=(
            "Ensure the HTML report meets PIF tone standards and all recommendations "
            "have a responsible party and timeline."
        ),
        backstory=(
            "Editorial lead at Pahlé India Foundation. You fix: prohibited negative words, "
            "em-dashes/en-dashes, recommendations missing responsible party or timeline, "
            "and claims with no number. Output corrected HTML only."
        ),
        llm=ALT_MODEL,
        verbose=False,
        allow_delegation=False,
        max_iter=1,
        tools=[],
    )


def make_task(agent: Agent, division_id: str, writer_snippet: str) -> Task:
    return Task(
        description=(
            "Review and fix the HTML report below.\n\n"
            f"REPORT TO REVIEW:\n{writer_snippet}\n\n"
            "FIX IN ONE PASS:\n"
            "1. Prohibited words: failing/failure/struggling/poor performance/"
            "inadequate/weak/disappointing/alarming → replace with "
            "'has scope for improvement' or 'requires focused attention'.\n"
            "2. Em-dashes (--) or en-dashes: replace with comma or full stop.\n"
            "3. Recommendations missing responsible party or timeline: add them.\n"
            "4. Claims with no number: add a number from the data.\n\n"
            "OUTPUT: Return the COMPLETE corrected HTML starting with <!DOCTYPE html>. "
            "No commentary. No markdown fences."
        ),
        expected_output=(
            "Complete corrected HTML document starting with <!DOCTYPE html>. "
            "No additional text."
        ),
        agent=agent,
    )
