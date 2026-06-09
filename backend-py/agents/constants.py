"""
Shared constants for all CrewAI agents.
"""

# Groq free tier: llama-3.3-70b-versatile = 12k TPM (single large request exceeds it)
# llama-3.1-8b-instant = 131k TPM — use for all agents until Groq Dev tier is active
FAST_MODEL   = "groq/llama-3.1-8b-instant"
STRONG_MODEL = "groq/llama-3.1-8b-instant"

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
