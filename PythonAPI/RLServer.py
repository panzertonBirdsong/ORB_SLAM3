import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
# from torchvision import datasets, transforms
# from torch.utils.data import DataLoader
# from image_reader.image_reader import ImageReader
import time
import pyRAPL
import socket
import selectors
import random
import json
import gymnasium as gym
import numpy as np
from gymnasium import spaces
import docker



class RLServer(gym.Env):

	def __init__(self, max_steps=2**63-1, verbose=False, train=True):
		super().__init__()

		self.max_steps = max_steps
		self.verbose = verbose
		self.train = train

		self.port = 5000
		self.host = "0.0.0.0"

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind((self.host, self.port))
		self.socket.listen(20)
		self.last_sock = None
		self.last_addr = None

		self.action_space = gym.spaces.Box(low=np.array([600, 0.8, 8, 16, 3]),
											high=np.array([2000, 1.4, 15, 30, 11]),
											dtype=np.float32)
		

		obs_highs = np.array(
			[2**63 - 2] +           # TimeStamp
			[1] * 6 +               # TrackMode one-hot-encoded
			[1.0] * 4 +             # Brightness, Contrast, Entropy, Laplacian
			[1e5] * 3 +             # MatchedInlier, NumberKeyPoints, NumberKeyFrame
			[1e3] * 7 +             # PX–QW
			[1e2] * 3 +             # DX–DZ
			[3.14] * 3              # Yaw–Roll (±pi)
		)
		
		obs_lows = np.zeros_like(highs)

		self.obs_template = obs_lows

		self.observation_space = gym.spaces.Box(low=obs_lows, high=obs_highs, dtype=np.float32)

		self.reward = 0.0
		self.steps = 0
		self.itr = 0

		self.start_time = time.time()


	def encode_track_mode(mode):
		sensor_types = [
			"MONOCULAR",
			"STEREO",
			"RGBD",
			"IMU_MONOCULAR",
			"IMU_STEREO",
			"IMU_RGBD"
		]

		if mode not in sensor_types:
			raise ValueError(f"Unknown sensor type: {mode}")

		result = [1 if mode == sensor else 0 for mode in sensor_types]
		return result


	# # return the cumulative reward for current time frame
	# # set self.reward = 0
	# def get_reward(self):
	# 	reward = self.reward
	# 	self.reward = 0.0
	# 	return reward

	def calculate_reward(self, obs):
		...
		return 0


	def encode_action(action):
		...
		return encoded_action

	def decode_msg(msg_str):

		msg = msg_str.decode('utf-8')

		if msg == "SLAM_initialized":
			return "initialized", None
		elif msg == "SLAM_shutdown":
			return "shutdown", None
		else:
			request_type = "request_action"
			obs_str = msg.split(",")
			obs = []
			for i in range(len(obs_str)):
				if i == 1:
					obs.append(self.encode_track_mode(obs_str[i]))
				else:
					obs.append(float(obs_str[i]))
			return request_type, np.array(obs)

	def clip_action(self, action):
		low = np.array([600, 0.8, 8, 15, 3])
		high = np.array([2000, 1.4, 16, 30, 11])
		action = np.clip(action, low, high)

		for i in range(len(action)):
			if i != 1:
			action[i] = int(round(action[i]))
		return action

	def step(self, action):
		self.steps = self.steps + 1
		action = self.clip_action(action)

		if self.verbose:
			print(f"\tSteps: {self.steps}\n", flush=True)


		# reply decision if task_request is received in previous step
		if self.request_not_replied:

			if self.verbose:
				print(f"\t action: {action}", flush=True)

			# decision = json.dumps({"type": "decision", "target_server": int(action), "expected_latency": expected_latency})
			encoded_action = self.encode_action(action)
			# self.last_sock.sendall(decision.encode('utf-8'))
			self.last_sock.sendall(encode_action)
			self.last_sock.close()
			self.request_not_replied = False

		while True:

			client_socket, client_addr = self.socket.accept()
			msg_str = client_socket.recv(1024)
			request_type, obs = self.decode_msg(msg_str)


			if request_type == "initialized":
				...
				continue
			elif request_type == "shutdown":
				self.request_not_replied = True
				self.last_sock = client_socket
				self.last_addr = client_addr
				return self.obs_template, self.calculate_reward(obs), True, False, None
			else:


				if self.verbose:
					print(f"\t {request}", flush=True)

				self.request_not_replied = True

				# observation = self.decode_obs(request)
				# reward = self.get_reward(request)
				reward = self.calculate_reward(obs)

				self.last_sock = client_socket
				self.last_addr = client_addr

				if self.verbose:
					print(f"\t\treward: {reward}")
				return obs, reward, False, False, {f"itr": self.itr}


	def reset(self, seed=None, options=None):

		if self.verbose:
			print("\nReset: system reset\n", flush=True)


		self.__init__()



		observation = self.obs_template

		self.just_reset = True
		self.request_not_replied = False

		return observation, {"type": "reset"}

	# this function is required by gym, but we do not need this function.
	def render(self):
		...

	def close(self):
		...
		# for name in self.containers:
		# 	try:
		# 		container = self.client.containers.get(name)
		# 		container.stop()
		# 		container.remove()
		# 	except Exception as e:
		# 		print(f"Error cleaning up container {container.name}: {e}")


