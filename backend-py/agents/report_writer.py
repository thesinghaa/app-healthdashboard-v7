"""
Agent 3 — ReportWriter
Model: STRONG_MODEL (KEY1, new window after 20s pace)
Job:   Write full self-contained HTML report with PIF styling.
Context injected via task description strings (not CrewAI context=[...]).
"""

from crewai import Agent, Task
from .constants import STRONG_MODEL, TONE_RULES
from tools.agent_tools import generate_charts_tool


def make_agent() -> Agent:
    return Agent(
        role="Senior Health Report Writer",
        goal=(
            "Produce a polished HTML report on division performance "
            "suitable for a senior NHM officer."
        ),
        backstory=(
            "You write executive health reports for government health departments "
            "in India on behalf of Pahlé India Foundation. Clean, self-contained "
            "HTML with inline CSS. Constructive tone. Exact numbers in every claim. "
            "Never use em-dashes. Gap = 'has scope for improvement'."
        ),
        llm=STRONG_MODEL,
        verbose=False,
        allow_delegation=False,
        max_iter=1,
        tools=[generate_charts_tool],
    )


def make_task(agent: Agent, division_id: str, div_full_name: str,
              dc_snippet: str, analyst_snippet: str) -> Task:
    return Task(
        description=(
            f"Write a complete HTML report for {div_full_name} division, "
            f"NHM Arunachal Pradesh, FY 2025-26.\n\n"
            f"DATA SUMMARY:\n{dc_snippet}\n\n"
            f"ANALYSIS:\n{analyst_snippet}\n\n"
            f"CHARTS: Call 'Generate Charts' tool with division_id='{division_id}' "
            "first. Use placeholder comments where charts should appear.\n\n"
            "REQUIRED SECTIONS (all 8 mandatory):\n"
            "1. COVER: division name, 'NHM Arunachal Pradesh', 'Pahlé India Foundation', "
            "   today's date, 'FY 2025-26 Performance Report'.\n"
            "2. EXECUTIVE SUMMARY: 2-3 sentences with exact numbers.\n"
            "3. DIVISION SCORECARD: HTML table — Programme | Status | KDs | Key Metric.\n"
            "4. CRITICAL PRIORITIES: one card per critical programme.\n"
            "5. WHAT IS WORKING: 3 bright spots in a grid.\n"
            "6. HMIS TREND OBSERVATIONS: bullet list.\n"
            "7. STRATEGIC RECOMMENDATIONS: 6 numbered items, each with responsible "
            "   party and timeline.\n"
            "8. DATA APPENDIX: full KD table.\n\n"
            "STYLING: Self-contained HTML, all CSS in <style>. Background #f0f2f5, "
            "cards white, PIF orange #FF5500 accents. Max-width 900px centered. "
            "Status badges: Critical=bg#fee2e2/text#991b1b, Caution=bg#fef3c7/text#92400e, "
            "On Track=bg#d1fae5/text#065f46. Font: Inter from Google Fonts.\n\n"
            f"{TONE_RULES}"
        ),
        expected_output=(
            "A complete valid HTML document starting with <!DOCTYPE html> "
            "with all 8 sections, inline CSS, PIF styling, chart placeholders."
        ),
        agent=agent,
    )
