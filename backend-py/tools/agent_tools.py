"""
CrewAI @tool wrappers — lets agents call kd_loader, hmis_fetcher, chart_gen autonomously.
"""

import json
from crewai.tools import tool

from .kd_loader    import get_division_summary, get_raw_division
from .hmis_fetcher import fetch_hmis_summary
from .chart_gen    import generate_all_charts


@tool("KD Summary")
def kd_summary_tool(division_id: str) -> str:
    """Returns a ~700-token text summary of KD performance for a division.
    division_id must be one of: rch, ndcp, ncd, hss, hrh.
    Includes: division snapshot, per-programme status, top-5 critical gaps, top-3 achievements."""
    return get_division_summary(division_id)


@tool("KD Raw Data")
def kd_raw_tool(division_id: str) -> str:
    """Returns the full KD indicator tree as JSON for a division.
    Use for deep lookups — exact targets, achievements, numerators, denominators.
    division_id must be one of: rch, ndcp, ncd, hss, hrh."""
    return json.dumps(get_raw_division(division_id), ensure_ascii=False)


@tool("HMIS Trends")
def hmis_trends_tool(division_id: str) -> str:
    """Fetches live HMIS monthly trend data for a division from the state health portal.
    Returns text summary of last 6 months for key indicators.
    division_id must be one of: rch, ndcp, ncd, hss, hrh."""
    return fetch_hmis_summary(division_id)


@tool("Generate Charts")
def generate_charts_tool(division_id: str) -> str:
    """Generates programme status donut, critical KDs bar, and scorecard charts for a division.
    Returns which chart keys are available.
    Use these EXACT placeholder comments in the HTML output:
      <!--CHART:status_donut-->
      <!--CHART:critical_kds-->
      <!--CHART:scorecard-->
    division_id must be one of: rch, ndcp, ncd, hss, hrh."""
    raw = get_raw_division(division_id)
    charts = generate_all_charts(raw)
    available = [k for k, v in charts.items() if v]
    if not available:
        return "No charts could be generated for this division."
    return (
        f"Charts generated successfully. Available: {available}. "
        f"Insert these placeholder comments exactly in the HTML where each chart should appear: "
        + ", ".join(f"<!--CHART:{k}-->" for k in available)
    )
