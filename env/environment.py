import json
from agent.baseline import analyze_code


class CodeReviewEnv:
    def __init__(self):
        self.tasks = {
            "easy": json.load(open("data/easy.json")),
            "medium": json.load(open("data/medium.json")),
            "hard": json.load(open("data/hard.json"))
        }

        self.task_names = ["easy", "medium", "hard"]
        self.current_task_idx = 0
        self.sample_idx = 0  # ✅ NEW

    def reset(self):
        self.current_task_idx = 0
        self.sample_idx = 0

        task = self.task_names[self.current_task_idx]
        sample = self.tasks[task][self.sample_idx]

        return {
            "code": sample["code"],
            "task": task
        }

    def step(self, action=None):
        task = self.task_names[self.current_task_idx]
        sample = self.tasks[task][self.sample_idx]

        obs = {
            "code": sample["code"],
            "language": sample["language"],
            "context": sample.get("context", "")
        }

        result = analyze_code(obs)
        predicted = result.get("issues", [])

        expected = sample.get("issues", [])

        correct = sum(
            1 for p in predicted
            if any(p["type"] == e["type"] and p["line"] == e["line"] for e in expected)
        )

        # ✅ SAFE REWARD
        reward = (correct + 0.5) / (len(expected) + 1)

        # 🔥 MOVE TO NEXT SAMPLE
        self.sample_idx += 1

        # If no more samples → move to next task
        if self.sample_idx >= len(self.tasks[task]):
            self.current_task_idx += 1
            self.sample_idx = 0

        done = self.current_task_idx >= 3

        if not done:
            next_task = self.task_names[self.current_task_idx]
            next_sample = self.tasks[next_task][self.sample_idx]

            next_obs = {
                "code": next_sample["code"],
                "task": next_task
            }
        else:
            next_obs = None

        return next_obs, reward, done, {}
