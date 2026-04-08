from fastapi import FastAPI
from env.environment import CodeReviewEnv

app = FastAPI()

env = None


@app.post("/openenv/reset")
def reset():
    global env
    env = CodeReviewEnv()
    obs = env.reset()

    return {
        "observation": obs
    }


@app.post("/openenv/step")
def step():
    global env

    if env is None:
        return {"error": "Environment not initialized"}

    obs, reward, done, info = env.step()

    return {
        "observation": obs,
        "reward": float(reward),
        "done": bool(done),
        "info": info
    }