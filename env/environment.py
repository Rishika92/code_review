import json
from agent.baseline import analyze_code

# ✅ Pydantic models
from pydantic import BaseModel
from typing import List, Optional


class Issue(BaseModel):
    type: str
    line: int
    message: str


class Observation(BaseModel):
    code: str
    language: str
    context: Optional[str]


class Action(BaseModel):
    issues: List[Issue]


class Reward(BaseModel):
    score: float


class CodeReviewEnv:
    def __init__(self, data_path="data/hard.json"):
        with open(data_path, "r") as f:
            self.data = json.load(f)

        self.index = 0
        self.current_sample = None

    # 🔄 Reset environment
    def reset(self):
        self.index = 0
        self.current_sample = self.data[self.index]

        return {
            "code": self.current_sample.get("code", ""),
            "language": self.current_sample.get("language", ""),
            "context": self.current_sample.get("context", "")
        }

    # ⚡ Step function
    def step(self, action=None):
        sample = self.current_sample

        # If no external action, use baseline agent
        if action is None:
            obs = {
                "code": sample.get("code", ""),
                "language": sample.get("language", ""),
                "context": sample.get("context", "")
            }
            result = analyze_code(obs)
            predicted = result.get("issues", [])
        else:
            predicted = action if isinstance(action, list) else []

        expected = sample.get("issues", [])

        # 🔢 Reward calculation
        correct = 0
        for p in predicted:
            if any(p["type"] == e["type"] and p["line"] == e["line"] for e in expected):
                correct += 1

        reward = correct / len(expected) if expected else 0.0

        # ⚠️ Penalize over-detection
        if len(predicted) > len(expected):
            reward -= 0.1 * (len(predicted) - len(expected))

        reward = max(0.0, reward)

        # Move to next step
        self.index += 1
        done = self.index >= len(self.data)

        if not done:
            self.current_sample = self.data[self.index]
            next_obs = {
                "code": self.current_sample.get("code", ""),
                "language": self.current_sample.get("language", ""),
                "context": self.current_sample.get("context", "")
            }
        else:
            next_obs = None

        return next_obs, reward, done, {}

    # 📊 State
    def state(self):
        return {
            "current_index": self.index,
            "total_samples": len(self.data)
        }