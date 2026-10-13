"""Reads a class-action settlement notice and gets the key terms from an AI model.
The AI must quote the exact text it used for every value (the "evidence").

Three ways to run (all checked by the same controls in checks.py):
  1. Gemini API - FREE key from https://aistudio.google.com  (set GEMINI_API_KEY)
  2. Claude API - paid key from https://console.anthropic.com (set ANTHROPIC_API_KEY)
  3. Manual mode - FREE, no key: copy the prompt into claude.ai or gemini.google.com,
     then paste the AI's answer back into the app.
"""
import json
import os
import re

from fields import FIELDS

# Model names change over time. If you get a "model not found" error,
# check the provider's docs and update these.
GEMINI_MODEL = "gemini-2.5-flash"
CLAUDE_MODEL = "claude-sonnet-4-5"

PROMPT = """You read class-action settlement notices for an asset manager's operations team.
Extract these fields: {fields}.
Rules:
- Dates as YYYY-MM-DD. Money as a plain number with no symbols or commas.
- If a field is not in the notice, use null. Never guess.
- For each field, give "evidence": the exact short quote from the notice that supports it.
Return only JSON in this shape:
{{"fields": {{"case_name": "...", "...": "..."}}, "evidence": {{"case_name": "...", "...": "..."}}}}

NOTICE:
{text}"""


def read_notice(path):
    """Return the text of a PDF or TXT notice."""
    if path.lower().endswith(".pdf"):
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    with open(path, encoding="utf-8") as f:
        return f.read()


def build_prompt(text):
    return PROMPT.format(fields=", ".join(FIELDS), text=text[:150000])


def parse_json(raw):
    """Turn the AI's answer into a Python dict, even if it is wrapped in ``` fences."""
    raw = raw.strip()
    raw = re.sub(r"^```(json)?|```$", "", raw, flags=re.M).strip()
    start, end = raw.find("{"), raw.rfind("}")
    return json.loads(raw[start:end + 1])


def which_provider():
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        return "gemini"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "claude"
    return "manual"


def extract(text):
    """Call whichever API has a key set. Returns {"fields": {...}, "evidence": {...}}."""
    provider = which_provider()
    prompt = build_prompt(text)
    if provider == "gemini":
        from google import genai
        client = genai.Client()  # reads GEMINI_API_KEY
        resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return parse_json(resp.text)
    if provider == "claude":
        import anthropic
        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
        msg = client.messages.create(
            model=CLAUDE_MODEL, max_tokens=1500,
            messages=[{"role": "user", "content": prompt}])
        return parse_json(msg.content[0].text)
    raise RuntimeError("No API key set - use manual mode.")
