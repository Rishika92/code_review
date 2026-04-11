import os
import re
import json
from openai import OpenAI

# ── Injected by the validator — never hardcode these ──────────────────────────
API_BASE_URL = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME",   "Qwen/Qwen2.5-72B-Instruct")
API_KEY      = os.environ.get("API_KEY") or os.environ.get("HF_TOKEN", "no-key")

# ── Client MUST use the proxy base_url so calls are observed by the validator ──
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY,
)

SYSTEM_PROMPT = """You are an expert code reviewer. Analyze the provided code and return ONLY a valid JSON object — no markdown, no explanation, no extra text.

Use this exact structure:
{
  "issues": [
    {
      "type": "<bug|security|optimization>",
      "line": <integer>,
      "description": "<short description>"
    }
  ]
}

If there are no issues return: {"issues": []}

Rules:
- "type" must be exactly one of: bug, security, optimization
- "line" must be an integer (the 1-based line number where the issue appears)
- Keep descriptions concise (under 10 words)
"""


def _llm_analyze(code: str, language: str = "python", context: str = "") -> dict:
    """Call the LLM proxy and parse the JSON response."""
    user_msg = f"Language: {language}\n"
    if context:
        user_msg += f"Context: {context}\n"
    user_msg += f"\nCode:\n```{language}\n{code}\n```"

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_msg},
        ],
        max_tokens=1024,
        temperature=0.1,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if model wrapped output in ```json ... ```
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    result = json.loads(raw)

    if "issues" not in result or not isinstance(result["issues"], list):
        return {"issues": []}

    # Normalise keys — LLM sometimes uses "message" instead of "description"
    clean = []
    for issue in result["issues"]:
        if not isinstance(issue, dict):
            continue
        issue_type = str(issue.get("type", "bug")).lower()
        if issue_type not in ("bug", "security", "optimization"):
            issue_type = "bug"
        clean.append({
            "type":        issue_type,
            "line":        int(issue.get("line", 1)),
            "description": str(
                issue.get("description") or issue.get("message", "")
            ),
        })

    return {"issues": clean}


def _rule_fallback(code: str) -> dict:
    """
    Lightweight rule-based fallback used ONLY when the LLM call fails.
    Keeps the env runnable even without network access.
    """
    issues = []
    seen   = set()

    for i, line in enumerate(code.split("\n"), start=1):
        ll = line.lower()

        checks = [
            (re.search(r"password\s*=\s*['\"]", ll),  "security",     "Hardcoded password"),
            ("eval("         in ll,                    "security",     "Dangerous eval usage"),
            ("select" in ll and "+" in ll,             "security",     "Possible SQL injection"),
            (re.search(r"except\s*:",  ll),            "bug",          "Bare except clause"),
            ("range(len"     in ll,                    "optimization", "Use enumerate instead"),
            ("append("       in ll,                    "optimization", "Consider list comprehension"),
        ]

        for condition, itype, msg in checks:
            if condition:
                key = (itype, i)
                if key not in seen:
                    seen.add(key)
                    issues.append({"type": itype, "line": i, "description": msg})

    return {"issues": issues}


def analyze_code(obs: dict) -> dict:
    """
    Main entry point called by environment.py.
    Tries the LLM proxy first; falls back to regex rules only on failure.
    """
    code     = obs.get("code", "")
    language = obs.get("language", "python")
    context  = obs.get("context", "")

    if not code.strip():
        return {"issues": []}

    try:
        result = _llm_analyze(code, language, context)
        print(f"[BASELINE] LLM returned {len(result['issues'])} issue(s)", flush=True)
        return result

    except json.JSONDecodeError as e:
        print(f"[BASELINE] JSON parse error: {e} — using rule fallback", flush=True)
        return _rule_fallback(code)

    except Exception as e:
        print(f"[BASELINE] LLM call failed: {e} — using rule fallback", flush=True)
        return _rule_fallback(code)
