import json
from agent.baseline import analyze_code

with open("data/easy.json") as f:
    data = json.load(f)

print("Loaded samples:", len(data))  # 👈 ADD THIS

for sample in data:
    obs = {
        "code": sample["code"],
        "language": sample["language"],
        "context": sample["context"]
    }

    result = analyze_code(obs)

    print("\nID:", sample["id"])
    print("Predicted:", result)
    print("Expected:", sample["issues"])