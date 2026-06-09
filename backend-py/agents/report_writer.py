"""
Agent 3 — ReportWriter
Model: strong (llama-3.3-70b-versatile)
Job:   Write full self-contained HTML report with PIF styling.
"""

from crewai import Agent, Task
from .constants import STRONG_MODEL, TONE_RULES
from tools.agent_tools import generate_charts_tool


def make_agent() -> Agent:
    return Agent(
        role="Senior Health Report Writer",
        goal=(
            "Produce a polished, authoritative HTML report on division performance, "
            "suitable for a senior NHM officer to read, present, and share with "
            "state and district health teams."
        ),
        backstory=(
            "You write executive health reports for government health departments "
            "in India on behalf of Pahlé India Foundation. Your reports are clear, "
            "data-driven, and structured so a busy district officer can act on them "
            "in under 10 minutes. You produce clean, self-contained HTML with inline "
            "CSS. Your tone is always constructive and professional. You never frame "
            "gaps as failures. You use exact indicator names and numbers in every claim. "
            "You never use em-dashes. The style guide says: gap = "
            "'has scope for improvement', not 'is failing'."
        ),
        llm=STRONG_MODEL,
        verbose=False,
        allow_delegation=False,
        max_iter=2,
        tools=[generate_charts_tool],
    )


def make_task(agent: Agent, division_id: str,
              div_full_name: str, context: list) -> Task:
    return Task(
        description=(
            f"Write a complete HTML report for {div_full_name} division, "
            f"NHM Arunachal Pradesh, FY 2025-26.\n\n"
            "Use ALL data from the briefing and analysis in the context.\n\n"
            f"CHARTS: Call the 'Generate Charts' tool with division_id='{division_id}' "
            "to see which charts are available, then use the placeholder comments "
            "it returns at the appropriate places in the HTML.\n\n"
            "REQUIRED SECTIONS (all 8 are mandatory):\n"
            "1. COVER / HEADER: division name in large type, 'NHM Arunachal Pradesh', "
            "   'Pahlé India Foundation', today's date, 'FY 2025-26 Performance Report'.\n"
            "2. EXECUTIVE SUMMARY: 2 to 3 sentences. Overall division health, "
            "   headline finding, top priority area. Use exact numbers.\n"
            "3. DIVISION SCORECARD: HTML table with columns — Programme | Status badge "
            "   | KDs Achieved/Total | Key Metric | Trend arrow.\n"
            "4. CRITICAL PRIORITIES: one styled card per critical programme. "
            "   Each card: programme name, what the data shows (exact numbers), "
            "   contributing factors, what focused attention is required.\n"
            "5. WHAT IS WORKING: 3 bright spots in a grid. Each: indicator name, "
            "   achievement value vs target, why it matters.\n"
            "6. HMIS TREND OBSERVATIONS: bullet list of monthly data patterns, "
            "   recent trajectory, seasonal notes.\n"
            "7. STRATEGIC RECOMMENDATIONS: numbered list, 6 items. "
            "   Each: action | Responsible: [party] | Timeline: [X weeks/months].\n"
            "8. DATA APPENDIX: full KD table — Programme | Indicator | Target | "
            "   Achievement | Status badge.\n\n"
            "STYLING (strict):\n"
            "- Self-contained HTML, all CSS in a <style> block.\n"
            "- Background #f0f2f5, card background #ffffff, "
            "  PIF orange #FF5500 for accents and headings.\n"
            "- Status badges: Critical = bg #fee2e2 text #991b1b, "
            "  Caution = bg #fef3c7 text #92400e, "
            "  On Track = bg #d1fae5 text #065f46.\n"
            "- Font: Inter (load from Google Fonts). Max width 900px centered.\n"
            "- Section headings: bold, #FF5500 left border accent.\n"
            "- For chart placeholders output exactly: <!--CHART:status_donut--> etc.\n"
            "- Valid HTML only. No markdown. No external images except Google Fonts.\n\n"
            f"{TONE_RULES}"
        ),
        expected_output=(
            "A complete, valid HTML document (starting with <!DOCTYPE html>) "
            "with all 8 sections, inline CSS, PIF styling, and chart placeholders."
        ),
        agent=agent,
        context=context,
    )
