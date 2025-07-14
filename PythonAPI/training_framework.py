import gymnasium as gym
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import PPO, DDPG, A2C
import RLServer.RLServer as Sys
import time
import random







def train():
	env = Sys()

	start_time = time.time()

	model = PPO("MlpPolicy",
		env,
		n_steps=128,
		verbose=1,
		tensorboard_log="logs/tppo/",
		device="cuda",
		policy_kwargs=policy_kwargs,
	)

	model.learn(total_timesteps=20000, log_interval=1)
	model.save("saved_models")
	print("Training done!", flush=True)

	end_time = time.time()
	t = end_time - start_time
	print(f"Total time: {t}", flush=True)


def eval():
	env = Sys(train=False)
	...