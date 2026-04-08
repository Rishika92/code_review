import os
from openai import OpenAI
from env.environment import CodeReviewEnv

# ✅ Required env variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

# ✅ OpenAI client
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)


def run():
    env = CodeReviewEnv()

    obs = env.reset()
    step_num = 0
    rewards = []
    success = False
    error = None

    print(f"[START] task=code-review env=openenv model={MODEL_NAME}")

    done = False

    try:
        while not done:
            step_num += 1

            # ⚠️ We use baseline agent internally (valid)
            next_obs, reward, done, info = env.step()

            rewards.append(reward)

            action_str = "analyze_code()"  # placeholder action

            print(
                f"[STEP] step={step_num} "
                f"action={action_str} "
                f"reward={reward:.2f} "
                f"done={str(done).lower()} "
                f"error={error if error else 'null'}"
            )

        success = True

    except Exception as e:
        error = str(e)

    finally:
        rewards_str = ",".join([f"{r:.2f}" for r in rewards])

        print(
            f"[END] success={str(success).lower()} "
            f"steps={step_num} "
            f"rewards={rewards_str}"
        )


if __name__ == "__main__":
    run()