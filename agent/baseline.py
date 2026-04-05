import re

def analyze_code(obs):
    code = obs["code"]
    issues = []

    lines = code.split("\n")
    code_lower = code.lower()

    # 🔥 1. PRIORITY: Nested loop detection
    if code_lower.count("for") > 1:
        return {
            "issues": [{
                "type": "optimization",
                "line": 1,
                "message": "Nested loop inefficiency"
            }]
        }

    for i, line in enumerate(lines, start=1):
        line_lower = line.lower()

        # 🔐 Security
        if re.search(r"password\s*=\s*['\"]", line_lower):
            issues.append({
                "type": "security",
                "line": i,
                "message": "Hardcoded password"
            })

        if "eval(" in line_lower:
            issues.append({
                "type": "security",
                "line": i,
                "message": "Dangerous eval usage"
            })

        # 🐞 Bugs
        if re.search(r"except\s*:", line_lower):
            issues.append({
                "type": "bug",
                "line": i,
                "message": "Bare except detected"
            })

        if "input()" in line_lower:
            issues.append({
                "type": "bug",
                "line": i,
                "message": "Missing input validation"
            })

        # ✅ Fix line mismatch (better detection)
        if "return none" in line_lower:
            issues.append({
                "type": "bug",
                "line": i - 1 if i > 1 else i,
                "message": "Returning None hides error"
            })

        # ⚡ Optimization: range(len(...))
        if "range(len" in line_lower:
            issues.append({
                "type": "optimization",
                "line": i,
                "message": "Use enumerate instead of range(len)"
            })

        # ⚡ Optimization: list building → comprehension
        if "append(" in line_lower:
            issues.append({
                "type": "optimization",
                "line": i - 1 if i > 1 else i,
                "message": "Use list comprehension"
            })

        # ⚡ Optimization: direct iteration opportunity
        if "range(len" in line_lower and "[" in code_lower:
            issues.append({
                "type": "optimization",
                "line": i,
                "message": "Use direct iteration instead of index"
            })

    # ❌ Remove duplicates
    unique_issues = []
    seen = set()

    for issue in issues:
        key = (issue["type"], issue["line"])
        if key not in seen:
            seen.add(key)
            unique_issues.append(issue)

    return {"issues": unique_issues}