# Define the shell script content
shell_script_template = "./Examples/Monocular/mono_tum_vi ./Vocabulary/ORBvoc.txt ./Examples/Monocular/SenseTime.yaml ./datasets/SenseTime/{}/camera/images ./Examples/Monocular/SenseTime_TimeStamps/{}.txt"

# Define the file name
file_name = "../run_RL_benchmark.sh"

trajectories = ["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", \
                             "B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"]

trials = 3

# Write the content to the file
with open(file_name, "w") as file:
    for i, traj in enumerate(trajectories):
        for j, trial in enumerate(range(trials)):
            file.write(shell_script_template.format(traj, traj) + "\n")
            file.write("sleep 10 \n")
            file.write("\n")

print(f"Shell script file '{file_name}' has been created.")
