import json
from agent.baseline import analyze_code

print("[START]")

data = json.load(open("data/hard.json"))

total_score = 0
total_cases = len(data)

for sample in data:
    print(f"[STEP] id={sample['id']}")

    obs = {
        "code": sample["code"],
        "language": sample["language"],
        "context": sample.get("context", "")
    }

    result = analyze_code(obs)

    predicted = result["issues"]
    expected = sample["issues"]

    # ✅ Compute score
    correct = 0
    for p in predicted:
        if any(p["type"] == e["type"] and p["line"] == e["line"] for e in expected):
            correct += 1

    score = correct / len(expected) if expected else 0
    total_score += score

    print({
        "predicted": result,
        "expected": expected,
        "score": round(score, 2)
    })

# ✅ Final score
final_score = total_score / total_cases if total_cases else 0
print(f"\nFinal Score: {round(final_score, 2)}")

print("[END]")