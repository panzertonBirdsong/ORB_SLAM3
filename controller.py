import subprocess
import socket
import shutil
import os

# This controller is to communicate with RLServer and (re)start and shutdown the SLAM process.
class SLAMController:
	def __init__(self, cmd, verbose=False):
		self.cmd = cmd
		self.verbose = verbose

	def run_slam(self):
		# cmd_list = ["xvfb-run", "-s", "-screen 0 1280x720x24"] + self.cmd.split()
		
		cmd_list = [
			"xvfb-run", "-a",
			"-s", "-screen 0 1280x720x24"
		] + self.cmd.split()


		pSLAM = subprocess.Popen(
			cmd_list,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE
		)

		if self.verbose:
			print("Start a new SLAM process.")
		
		# return pSLAM.pid

		# pSLAM.wait()

		stdout, stderr = pSLAM.communicate()

		with open("slam_output.log", "a") as f:
			f.write("\n\n===== New Run =====\n")
			f.write("=== STDOUT ===\n")
			f.write(stdout.decode(errors="replace"))
			f.write("\n=== STDERR ===\n")
			f.write(stderr.decode(errors="replace"))


		exit_code = pSLAM.returncode
		return exit_code

	def communicate_with_server(self, msg, host="127.0.0.1", port=5000):
		try:
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
				s.settimeout(120.0)
				s.connect((host, port))
				s.sendall(msg.encode('utf-8'))
				response = s.recv(1024).decode('utf-8')
				if self.verbose:
					print(f"MSG sent: {msg}\nMSG received: {response}")
				return response
		except socket.timeout:
			return "TIMEOUT"
			# exit()
		except Exception as e:
			if self.verbose:
				print(f"Error: {e}")
			return "ERROR"

	def run(self):
		
		while True:

			response_0 = self.communicate_with_server("SLAM_initialized")
			if response_0 != "RLServer_Initialized":
				# exit()
				continue
			result = self.run_slam()
			if result == 0:
				response_1 = self.communicate_with_server("SLAM_success_shutdown")
			else:
				response_1 = self.communicate_with_server("SLAM_fail_shutdown")

			# if response_1 == "terminate":
			# 	break



if __name__ == '__main__':
	cmd = "./Examples/Stereo-Inertial/stereo_inertial_euroc ./Vocabulary/ORBvoc.txt ./Examples/Stereo-Inertial/EuRoC.yaml /home/pzt/Documents/Research/SLAM/EuRoc/MH_03_medium ./Examples/Stereo-Inertial/EuRoC_TimeStamps/MH03.txt dataset-MH03_stereoi"

	slam_controller = SLAMController(cmd, verbose=True)
	slam_controller.run()