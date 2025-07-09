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

from evo_helper import evo_eval



class RLServer(gym.Env):

	def __init__(self, max_steps=2**63-1, verbose=False, train=True, reward_type="evo", ground_truth_ref="./euroc_ref.csv"):
		super().__init__()

		self.max_steps = max_steps
		self.verbose = verbose
		self.train = train
		self.reward_type = reward_type
		self.ground_truth_ref = ground_truth_ref

		self.est_traj_file = "./est_traj.txt"
		if os.path.exists(self.est_traj_file):
			os.remove(self.est_traj_file)
		open(self.est_traj_file, 'w').close()



		self.port = 5000
		self.host = "127.0.0.1"

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

		self.last_cumulative_reward = 0.0
		self.steps = 0
		self.itr = 0

		self.start_time = time.time()

	def write_traj(self, obs):
		timestamp = obs[0]
		p_q = obs[14:21]
		assert p_q.shape[0] == 7, "Failed to write trajectory: incorrect shape."
		data = [f"{timestamp:.9f}"] + [f"{x:.6f}" for x in p_q]
		line = " ".join(values) + "\n"
		with open(self.est_traj_file, 'a') as f:
			f.write(line)


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

	def calculate_reward(self, obs, folder_name):
		
		if self.reward_type == "evo":
			new_cumulative_reward = evo_eval(folder_name, self.ground_truth_ref, self.est_traj_file)
			new_reward = new_cumulative_reward - self.last_cumulative_reward
			self.last_cumulative_reward = new_cumulative_reward
			return new_reward

		elif self.reward_type == "SEESys":
			...
		return 0


	def encode_action(self, action):
		...
		return encoded_action

	def decode_msg(self, msg_str):

		msg = msg_str.decode('utf-8')

		if msg == "SLAM_initialized":
			return "initialized", None
		elif msg == "SLAM_success_shutdown":
			return "shutdown", 0
		elif msg == "SLAM_fail_shutdown":
			return "shutdown", 1
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
				reply = "RLServer_Initialized"
				self.client_socket.sendall(reply.encode('utf-8'))
				self.client_socket.close()
			elif request_type == "shutdown":
				reply = "Server_Reset"
				self.client_socket.sendall(reply.encode('utf-8'))
				self.client_socket.close()
				if obs == 0:
					amplifier = 1
				else:
					amplifier = -2

				self.request_not_replied = True
				self.last_sock = client_socket
				self.last_addr = client_addr
				return self.obs_template, self.last_cumulative_reward*amplifier, True, False, None
			else:
				self.write_traj(obs)


				self.request_not_replied = True

				reward = self.calculate_reward(obs, f"step_{self.steps}")

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


