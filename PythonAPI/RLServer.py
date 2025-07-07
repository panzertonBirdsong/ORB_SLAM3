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
		self.last_client = None

		self.action_space = gym.spaces.Box(low=np.array([600, 0.8, 8, 15, 3]),
											high=np.array([2000, 1.4, 16, 30, 11]),
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


	# return the cumulative reward for current time frame
	# set self.reward = 0
	def get_reward(self):
		reward = self.reward
		self.reward = 0.0
		return reward

	# return the observation
	def get_state(self, client_status, task_size, latency_requirement):
		client_id_encoded = [0] * self.num_clients
		client_id_encoded[client_status] = 1
		states = (
			self.threads +
			self.workload +
			sum(self.network_status, []) +
			client_id_encoded +
			[task_size] +
			[latency_requirement]
		)

		return np.array(states, dtype=np.float32)

	def encode_action(action):
		...
		return encoded_action

	def decode_obs(obs):
		...
		return decoded_obs

	def step(self, action):
		self.steps = self.steps + 1

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
			data = client_socket.recv(1024)
			request = json.loads(data.decode('utf-8'))


			if request["type"] == "init":
				...
				continue
			elif request["type"] == 


			if self.verbose:
				print(f"\t {request}", flush=True)

			self.request_not_replied = True

			observation = self.decode_obs(request)
			reward = self.get_reward(request)

			self.last_sock = client_socket
			self.last_addr = client_addr

			if self.steps >= self.max_steps or request["terminate"] == True:
				terminated = True
				self.steps = 0

				print(f"Itr {self.itr} done, has run for {time.time() - self.start_time}s.", flush=True)
					
				self.itr += 1
			else:
				terminated = False

			if self.verbose:
				print(f"\t\treward: {reward}")
			return observation, reward, terminated, False, {f"itr": self.itr}


	def reset(self, seed=None, options=None):

		if self.verbose:
			print("\nReset: system reset\n", flush=True)


		self.__init__()



		observation = self.get_state(0,0,0)

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


