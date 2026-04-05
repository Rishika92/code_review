import re

def analyze_code(obs):
    code = obs["code"]
    issues = []

    lines = code.split("\n")

    for i, line in enumerate(lines, start=1):
        line_lower = line.lower()

        # 🔐 Security: Hardcoded password
        if re.search(r"password\s*=\s*['\"]", line_lower):
            issues.append({
                "type": "security",
                "line": i,
                "message": "Hardcoded password"
            })

        # 🔐 Security: eval usage
        if "eval(" in line_lower:
            issues.append({
                "type": "security",
                "line": i,
                "message": "Dangerous eval usage"
            })

        # 🐞 Bug: bare except
        if re.search(r"except\s*:", line_lower):
            issues.append({
                "type": "bug",
                "line": i,
                "message": "Bare except detected"
            })

        # ⚡ Optimization: range(len(...))
        if "range(len" in line_lower:
            issues.append({
                "type": "optimization",
                "line": i,
                "message": "Use enumerate instead of range(len)"
            })

    # ❌ Remove duplicate issues (important)
    unique_issues = []
    seen = set()

    for issue in issues:
        key = (issue["type"], issue["line"])
        if key not in seen:
            seen.add(key)
            unique_issues.append(issue)

    return {"issues": unique_issues}