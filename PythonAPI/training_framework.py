import gymnasium as gym
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import PPO, DDPG, A2C
from rl_server import RLServer
import time
import random







def train():
	env = RLServer(verbose=True)

	start_time = time.time()

	model = PPO("MlpPolicy", env, n_steps=5000, verbose=1, tensorboard_log="logs/ppo/", device="cpu")

	model.learn(total_timesteps=5000_0000, log_interval=1)
	model.save("saved_models")
	print("Training done!", flush=True)

	end_time = time.time()
	t = end_time - start_time
	print(f"Total time: {t}", flush=True)


def eval():
	env = Sys(train=False)
	...