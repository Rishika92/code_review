import json
from agent.baseline import analyze_code


class CodeReviewEnv:
    def __init__(self):
        self.task_names = ["easy", "medium", "hard"]
        self.tasks = {}
        for name in self.task_names:
            path = f"data/{name}.json"
            try:
                with open(path) as f:
                    self.tasks[name] = json.load(f)
                print(f"[ENV] Loaded {len(self.tasks[name])} samples from {path}", flush=True)
            except FileNotFoundError:
                print(f"[ENV ERROR] Missing file: {path}", flush=True)
                self.tasks[name] = []
            except json.JSONDecodeError as e:
                print(f"[ENV ERROR] Corrupt JSON in {path}: {e}", flush=True)
                self.tasks[name] = []

        self.current_task_idx = 0
        self.sample_idx = 0

    def reset(self):
        self.current_task_idx = 0
        self.sample_idx = 0
        task = self.task_names[self.current_task_idx]
        samples = self.tasks[task]
        if not samples:
            return {"code": "", "task": task}
        sample = samples[self.sample_idx]
        return {"code": sample["code"], "task": task}

    def step(self, action=None):
        task = self.task_names[self.current_task_idx]
        samples = self.tasks[task]

        # No data for this task — skip with a neutral non-zero reward
        if not samples:
            print(f"[ENV WARN] No samples for task '{task}', skipping.", flush=True)
            self.current_task_idx += 1
            self.sample_idx = 0
            done = self.current_task_idx >= len(self.task_names)
            # Return 0.001 (not 0.0) so the validator score stays inside (0, 1)
            return None, 0.001, done, {"warning": f"no samples for task {task}"}

        sample = samples[self.sample_idx]
        obs = {
            "code":     sample["code"],
            "language": sample.get("language", "python"),
            "context":  sample.get("context", "")
        }

        # Run analysis safely
        try:
            result    = analyze_code(obs)
            predicted = result.get("issues", [])
        except Exception as e:
            print(f"[STEP ERROR] analyze_code failed on {task}[{self.sample_idx}]: {e}", flush=True)
            predicted = []

        expected = sample.get("issues", [])

        correct = sum(
            1 for p in predicted
            if any(
                p.get("type") == e.get("type") and p.get("line") == e.get("line")
                for e in expected
            )
        )

        # Formula produces values in (0, 1) — never exactly 0 or 1
        # min value: (0 + 0.5) / (N + 1)  → approaches 0 but never reaches it
        # max value: (N + 0.5) / (N + 1)  → approaches 1 but never reaches it
        raw_reward = (correct + 0.5) / (len(expected) + 1)
        # Extra safety clamp
        reward = max(0.001, min(0.999, raw_reward))

        print(
            f"[STEP] task={task} sample={self.sample_idx} "
            f"correct={correct}/{len(expected)} reward={reward:.4f}",
            flush=True
        )

        # Advance to next sample / task
        self.sample_idx += 1
        if self.sample_idx >= len(self.tasks[task]):
            self.current_task_idx += 1
            self.sample_idx = 0

        done = self.current_task_idx >= len(self.task_names)

        if not done:
            next_task = self.task_names[self.current_task_idx]
            next_samples = self.tasks[next_task]
            if next_samples and self.sample_idx < len(next_samples):
                next_sample = next_samples[self.sample_idx]
                next_obs = {"code": next_sample["code"], "task": next_task}
            else:
                next_obs = {"code": "", "task": next_task}
        else:
            next_obs = None

        return next_obs, reward, done, {}
