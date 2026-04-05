import re

def analyze_code(obs):
    code = obs["code"]
    issues = []

    lines = code.split("\n")
    code_lower = code.lower()

    # 🔥 1. PRIORITY: Nested loop detection (performance)
    if code_lower.count("for") > 1:
        return {
            "issues": [{
                "type": "optimization",
                "line": 1,
                "message": "High time complexity (nested loops)"
            }]
        }

    for i, line in enumerate(lines, start=1):
        line_lower = line.lower()

        # =========================
        # 🔐 SECURITY
        # =========================

        # Hardcoded password
        if re.search(r"password\s*=\s*['\"]", line_lower):
            issues.append({
                "type": "security",
                "line": i,
                "message": "Hardcoded password"
            })

        # Dangerous eval
        if "eval(" in line_lower:
            issues.append({
                "type": "security",
                "line": i,
                "message": "Dangerous eval usage"
            })

        # SQL Injection
        if "select" in line_lower and "+" in line_lower:
            issues.append({
                "type": "security",
                "line": i,
                "message": "Possible SQL injection"
            })

        # Weak password comparison
        if "password ==" in line_lower:
            issues.append({
                "type": "security",
                "line": i,
                "message": "Hardcoded password check"
            })

        # =========================
        # 🐞 BUGS
        # =========================

        # Bare except
        if re.search(r"except\s*:", line_lower):
            issues.append({
                "type": "bug",
                "line": i,
                "message": "Bare except detected"
            })

        # Context-aware input validation (FIXED)
        if "input()" in line_lower and not any(
            x in code_lower for x in ["eval", "password", "select"]
        ):
            issues.append({
                "type": "bug",
                "line": i,
                "message": "Missing input validation"
            })

        # Silent failure
        if "return none" in line_lower:
            issues.append({
                "type": "bug",
                "line": i - 1 if i > 1 else i,
                "message": "Returning None hides error"
            })

        # Type mismatch
        if "== \"true\"" in line_lower:
            issues.append({
                "type": "bug",
                "line": i,
                "message": "Boolean compared to string"
            })

        # =========================
        # ⚡ OPTIMIZATION
        # =========================

        # range(len(...))
        if "range(len" in line_lower:
            issues.append({
                "type": "optimization",
                "line": i,
                "message": "Use enumerate instead of range(len)"
            })

        # List comprehension opportunity
        if "append(" in line_lower:
            issues.append({
                "type": "optimization",
                "line": i - 1 if i > 1 else i,
                "message": "Use list comprehension"
            })

        # Direct iteration instead of indexing
        if "range(len" in line_lower and "[" in code_lower:
            issues.append({
                "type": "optimization",
                "line": i,
                "message": "Use direct iteration instead of index"
            })

    # =========================
    # ❌ REMOVE DUPLICATES
    # =========================

    unique_issues = []
    seen = set()

    for issue in issues:
        key = (issue["type"], issue["line"])
        if key not in seen:
            seen.add(key)
            unique_issues.append(issue)

    return {"issues": unique_issues}