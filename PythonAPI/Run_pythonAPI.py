import socket
import time
import datetime

import random
import csv

# Configure the server IP and port
server_ip = "127.0.0.1"  # Listen on all available network interfaces
server_port = 10000

feature_name = ["TimeStamp", "TrackMode", "Brightness", "Contrast", "Entropy", "Laplacian",
                "MatchedInlier", "NumberKeyPoints", 
                "PX", "PY", "PZ", "QX", "QY", "QZ", "QW",
                "DX", "DY", "DZ", "Yaw", "Pitch", "Roll"]

action_name = ["RefRatio", "MinFrames", "MaxFrames"]
    
action_value_dict = {
    "RefRatio": [0.6, 0.7, 0.8, 0.9, 1.0],
    "MinFrames": [0, 1, 3, 5, 7, 10],
    "MaxFrames": [10, 20, 30, 40, 50, 60]    
}

def randomActionGenerator():
    RefRatio = random.choice(action_value_dict["RefRatio"])
    MinFrames = random.choice(action_value_dict["MinFrames"])
    MaxFrames = random.choice(action_value_dict["MaxFrames"])
    return [RefRatio, MinFrames, MaxFrames]

# def sendAction():
#     send_str = "1.1,2.2,3.3"
#     client_socket.send(bytes(send_str, encoding='utf-8'))
#     print("send:   {}".format(send_str))

# def receiveState():
#     recv_str = client_socket.recv(1024)
#     recv_str = recv_str.decode('utf-8')
#     # if not recv_str:
#     #     continue # skip the current loop
#     print("receive:{}".format(recv_str))

def write_row_csv(writer, row):
    writer.writerow(row)

def get_datetime():
    # Get the current date and time
    current_datetime = datetime.datetime.now()

    # Format the datetime as a string
    formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H-%M-%S")
    return formatted_datetime

# trajectories = ["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", \
#                              "B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"]

trajectories = ["A0", "A2", "A3", "A4", "A5", "A6", "A7", \
                             "B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"]

trials = 3

is_baseline = False      # Modify this variable for different mode
use_random_action = None
if is_baseline:
    use_random_action = False
else:
    use_random_action = True

idx = 0

while(True):
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))

    server_socket.listen(5)
    print(f"Listening on {server_ip}:{server_port}")
    print("Waiting for a connection...")

    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")

    send_str = "0.9,0,30"
    is_connected = False
    action_updated_time = time.time()
    
    #csv_file_name = get_datetime() + ".csv"
    csv_file_name = None
    traj_idx = idx // trials
    trial_idx = idx % trials
    if is_baseline:
        csv_file_name = "./Baselines/"+trajectories[traj_idx]+"_{}.csv".format(trial_idx)
    else:
        csv_file_name = "./RandomActions/"+trajectories[traj_idx]+"_{}.csv".format(trial_idx)
        

    idx += 1
    counter = 0
    # Open the CSV file in write mode and specify newline='' to avoid extra empty lines
    with open(csv_file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(feature_name+action_name)

        while True:
            recv_str = client_socket.recv(1024)
            recv_str = recv_str.decode('utf-8')
            current_time = time.time()
            if recv_str:
                is_connected = True
                if counter % 30 == 0:
                    print("receive:{}".format(recv_str))

                if (use_random_action):
                    # update the action every 3 seconds
                    if(current_time - action_updated_time >= 3.0):
                    #if(False):
                        actions = randomActionGenerator()
                        actions_str = [str(num) for num in actions]
                        actions_str = ",".join(actions_str)
                        send_str = actions_str
                        action_updated_time = current_time
                else:
                    action_updated_time = current_time

                client_socket.send(bytes(send_str, encoding='utf-8'))
                if counter % 30 == 0:
                    print("send:   {}".format(send_str))
                writer.writerow(recv_str.split(",") + send_str.split(","))

                counter += 1
            
            if((time.time()-action_updated_time >= 5.0) and is_connected):
                print("Current Connection End")
                break
            time.sleep(0.01)

    client_socket.close()
    server_socket.close()
    is_connected = False

    print("Current Trajectory End!")

exit()