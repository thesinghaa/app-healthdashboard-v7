"""
Shared constants for all CrewAI agents.

Groq free-tier: 6000 TPM per key per model per minute.
Strategy: alternate KEY1/KEY2 across agents so each key gets its own 6000 TPM budget.
  DC (KEY1) → Analyst (KEY2) → Writer (KEY1, new window) → QC (KEY2, new window)
"""
import os
from crewai import LLM

_KEY1 = os.getenv("GROQ_API_KEY", "")
_KEY2 = os.getenv("GROQ_API_KEY_2", "") or _KEY1   # falls back to KEY1 if KEY2 absent

_BASE_PARAMS = dict(
    model="groq/llama-3.1-8b-instant",
    max_tokens=2000,    # default; individual agents override via make_agent()
    temperature=0.3,
)
# Writer gets more output budget; others stay compact
WRITER_MAX_TOKENS = 3000

FAST_MODEL   = LLM(**_BASE_PARAMS, api_key=_KEY1)                          # DataCollector
ALT_MODEL    = LLM(**_BASE_PARAMS, api_key=_KEY2)                          # Analyst + QC
STRONG_MODEL = LLM(**{**_BASE_PARAMS, "max_tokens": WRITER_MAX_TOKENS},    # ReportWriter
                   api_key=_KEY1)

TONE_RULES = """
LANGUAGE RULES (strictly mandatory for all output):
- NEVER use: failing, failure, is failing, struggling, poor performance,
  inadequate, weak, disappointing, alarming, or any attacking/negative framing.
- Frame every gap as an opportunity: "has significant scope for improvement",
  "requires focused attention", "presents a clear opportunity to accelerate".
- NEVER use em-dashes (the character: —) or en-dashes (–). Use commas or
  full stops instead.
- Always reference exact indicator names and numbers from the data.
- Audience: senior NHM Arunachal Pradesh officers who need to act on this.
- Organisation: Pahlé India Foundation (PIF). Spell it exactly this way.
"""
