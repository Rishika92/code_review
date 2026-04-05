from fastapi import FastAPI
import json
from agent.baseline import analyze_code

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Code Review Environment Running"}

@app.get("/run")
def run_env():
    data = json.load(open("data/easy.json"))

    results = []

    for sample in data:
        obs = {
            "code": sample["code"],
            "language": sample["language"],
            "context": sample.get("context", "")
        }

        result = analyze_code(obs)

        results.append({
            "id": sample["id"],
            "predicted": result,
            "expected": sample["issues"]
        })

    return {"results": results}