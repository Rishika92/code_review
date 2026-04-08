from fastapi import FastAPI
from env.environment import CodeReviewEnv

app = FastAPI()

# Initialize environment globally
env = CodeReviewEnv()


@app.post("/openenv/reset")
def reset():
    obs = env.reset()
    return {
        "observation": obs
    }


@app.post("/openenv/step")
def step():
    next_obs, reward, done, info = env.step()

    return {
        "observation": next_obs,
        "reward": reward,
        "done": done,
        "info": info
    }
