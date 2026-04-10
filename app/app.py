from fastapi import FastAPI
from env.environment import CodeReviewEnv
import uvicorn

app = FastAPI()
_env = CodeReviewEnv()


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}


# ── Tasks list (REQUIRED by validator) ───────────────────────────────────────
@app.get("/tasks")
def list_tasks():
    return {
        "tasks": [
            {
                "id": "easy",
                "description": "Basic code review: detect simple bugs and syntax issues",
                "difficulty": "easy",
                "max_attempts": 5,
                "grader": "programmatic"
            },
            {
                "id": "medium",
                "description": "Intermediate: logical errors and code smells",
                "difficulty": "medium",
                "max_attempts": 5,
                "grader": "programmatic"
            },
            {
                "id": "hard",
                "description": "Advanced: security vulnerabilities and performance issues",
                "difficulty": "hard",
                "max_attempts": 5,
                "grader": "programmatic"
            }
        ]
    }


# ── Grader endpoint (REQUIRED by validator) ───────────────────────────────────
@app.post("/grader")
def run_grader(body: dict = None):
    """
    Run the grader for a specific task and return a score in (0.0, 1.0).
    Accepts: {"task_id": "easy"|"medium"|"hard"}
    """
    if body is None:
        body = {}

    task_id = body.get("task_id", "easy")
    if task_id not in ("easy", "medium", "hard"):
        task_id = "easy"

    env = CodeReviewEnv()
    obs = env.reset()

    # Fast-forward to the requested task
    task_names = ["easy", "medium", "hard"]
    target_idx = task_names.index(task_id)
    for _ in range(target_idx):
        _, _, done, _ = env.step()
        if done:
            break

    # Run one graded step on the target task
    _, reward, _, _ = env.step()

    # Clamp strictly inside (0, 1) — never exactly 0.0 or 1.0
    score = max(0.001, min(0.999, float(reward)))

    return {
        "task_id": task_id,
        "score": score,
        "success": score > 0.3
    }


# ── State ─────────────────────────────────────────────────────────────────────
@app.get("/state")
def state():
    return {"status": "ready", "tasks": ["easy", "medium", "hard"]}


# ── Reset ─────────────────────────────────────────────────────────────────────
@app.post("/reset")
def reset():
    env = CodeReviewEnv()
    obs = env.reset()
    return {"observation": str(obs)}


# ── Step ──────────────────────────────────────────────────────────────────────
@app.post("/step")
def step():
    env = CodeReviewEnv()
    obs = env.reset()
    done = False
    rewards = []
    step_count = 0
    error = None

    try:
        while not done:
            step_count += 1
            obs, reward, done, info = env.step()
            rewards.append(float(reward))
    except Exception as e:
        error = str(e)

    return {
        "success": error is None,
        "steps": step_count,
        "rewards": rewards,
        "error": error
    }


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
