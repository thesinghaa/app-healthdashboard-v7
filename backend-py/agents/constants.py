"""
Shared constants for all CrewAI agents.

Using Google Gemini 1.5 Flash — free tier, 1M TPM, no card required.
No pacing needed. All agents use same key and model.
"""
import os
from crewai import LLM

_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

_BASE_PARAMS = dict(
    model="gemini/gemini-1.5-flash",
    max_tokens=3000,
    temperature=0.3,
)

FAST_MODEL   = LLM(**_BASE_PARAMS, api_key=_GEMINI_KEY)
ALT_MODEL    = LLM(**_BASE_PARAMS, api_key=_GEMINI_KEY)
STRONG_MODEL = LLM(**_BASE_PARAMS, api_key=_GEMINI_KEY)

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
