import json
from agent.baseline import analyze_code

print("[START]")

data = json.load(open("data/hard.json"))

for sample in data:
    print(f"[STEP] id={sample['id']}")

    obs = {
        "code": sample["code"],
        "language": sample["language"],
        "context": sample.get("context", "")
    }

    result = analyze_code(obs)

    print({
        "predicted": result,
        "expected": sample["issues"]
    })

print("[END]")