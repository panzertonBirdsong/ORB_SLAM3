import os
import numpy as np
import pandas as pd
import copy
import tools

class Unity:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.benchmark = "Unity"
        self.scriptTemplate = None
        self.trajectories = None
        self.scriptList = []

    def generate_script(self):
        # self.scriptList = []
        # for i, trajectory in enumerate(self.trajectories):
        #     scriptDict = {}
        #     scriptDict["benchmark"] = self.benchmark
        #     scriptDict["trajectory"] = trajectory
        #     scriptTemp = copy.deepcopy(self.scriptTemplate)
        #     scriptTemp = scriptTemp.format(self.root_dir, self.root_dir, self.root_dir, \
        #                                    self.root_dir, trajectory, \
        #                                    self.root_dir, trajectory)
        #     scriptDict["script"] = scriptTemp
        #     self.scriptList.append(scriptDict)
        print("Unity dataset don't have scriptList")

    def get_script(self):
        return self.scriptList
    
    def copy_ground_truth_traj(self, trajectory):
        # gt_csv_path = "{}/datasets/SenseTime/{}/groundtruth/data.csv"
        # gt_csv_path = gt_csv_path.format(self.root_dir, trajectory)
        # df = pd.read_csv(gt_csv_path)
        # columns = ["#t[s:double]","p.x[m:double]", "p.y[m:double]", "p.z[m:double]", \
        #         "q.x[double]", "q.y[double]", "q.z[double]", "q.w[double]"]
        # df = df[columns]
        # df.to_csv("{}/logs/ground_truth.txt".format(self.root_dir), sep=' ', index=False, header=False)
        print("Please Copy the ground_truth.txt from Unity Generator to ORBSLAM_Prob")

    def load_n_save_estimated_traj(self):
        # Step 0: Read the CSV file
        df = pd.read_csv("{}/logs/log.csv".format(self.root_dir))
        
        for index, value in enumerate(df['TimeStamp'][1:-1], start=1):
            if(value == df.at[index+1, 'TimeStamp'] or value == 0 or value < df.at[index-1, 'TimeStamp']):
                df.at[index, 'TimeStamp'] = 0.5*(df.at[index-1, 'TimeStamp'] + df.at[index+1, 'TimeStamp'])
        #assert(df["TimeStamp"].is_monotonic_increasing)
        #assert(df["TimeStamp"].is_unique)

        # Step 2: Drop the rows of initialization
        target = 2
        initial_rows = (df["TrackMode"] == target).idxmax()
        initial_rows += 2
        df = df.iloc[initial_rows:].reset_index(drop=True)

        # Step 3: Select several columns by their names
        df_traj = copy.deepcopy(df)
        selected_columns = ["TimeStamp","PX","PY","PZ","QX","QY","QZ","QW"]  # Replace with your desired column names
        df_traj = df_traj[selected_columns]

        # Step 4: Save the DataFrame as a text (TXT) file
        df_traj.to_csv("{}/logs/trajectory.txt".format(self.root_dir), \
                       sep=' ', index=False, header=False)  
        # You can change the separator as needed
        return df, df_traj, initial_rows

class SenseTime:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.benchmark = "SenseTime"
        self.scriptTemplate = "{}/Examples/Monocular/mono_tum_vi {}/Vocabulary/ORBvoc.txt {}/Examples/Monocular/SenseTime.yaml {}/datasets/SenseTime/{}/camera/images {}/Examples/Monocular/SenseTime_TimeStamps/{}.txt"
        # self.trajectories = ["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", \
        #                      "B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"]
        self.trajectories = ["A0", "A2", "A3", "A4", "A5", "A6", "A7", \
                             "B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"]
        self.scriptList = []

    def generate_script(self):
        self.scriptList = []
        for i, trajectory in enumerate(self.trajectories):
            scriptDict = {}
            scriptDict["benchmark"] = self.benchmark
            scriptDict["trajectory"] = trajectory
            scriptTemp = copy.deepcopy(self.scriptTemplate)
            scriptTemp = scriptTemp.format(self.root_dir, self.root_dir, self.root_dir, \
                                           self.root_dir, trajectory, \
                                           self.root_dir, trajectory)
            scriptDict["script"] = scriptTemp
            self.scriptList.append(scriptDict)

    def get_script(self):
        return self.scriptList
    
    def copy_ground_truth_traj(self, trajectory):
        gt_csv_path = "{}/datasets/SenseTime/{}/groundtruth/data.csv"
        gt_csv_path = gt_csv_path.format(self.root_dir, trajectory)
        df = pd.read_csv(gt_csv_path)
        columns = ["#t[s:double]","p.x[m:double]", "p.y[m:double]", "p.z[m:double]", \
                "q.x[double]", "q.y[double]", "q.z[double]", "q.w[double]"]
        df = df[columns]
        df.to_csv("{}/logs/ground_truth.txt".format(self.root_dir), sep=' ', index=False, header=False)

    def load_n_save_estimated_traj(self):
        # Step 0: Read the CSV file
        df = pd.read_csv("{}/logs/log.csv".format(self.root_dir))
        
        for index, value in enumerate(df['TimeStamp'][1:-1], start=1):
            if(value == df.at[index+1, 'TimeStamp'] or value == 0 or value < df.at[index-1, 'TimeStamp']):
                df.at[index, 'TimeStamp'] = 0.5*(df.at[index-1, 'TimeStamp'] + df.at[index+1, 'TimeStamp'])
        #assert(df["TimeStamp"].is_monotonic_increasing)
        #assert(df["TimeStamp"].is_unique)

        # Step 2: Drop the rows of initialization
        target = 2
        initial_rows = (df["TrackMode"] == target).idxmax()
        initial_rows += 2
        df = df.iloc[initial_rows:].reset_index(drop=True)

        # Step 3: Select several columns by their names
        df_traj = copy.deepcopy(df)
        selected_columns = ["TimeStamp","PX","PY","PZ","QX","QY","QZ","QW"]  # Replace with your desired column names
        df_traj = df_traj[selected_columns]

        # replace Nan with 0
        df_traj.fillna(0, inplace=True)

        # Step 4: Save the DataFrame as a text (TXT) file
        df_traj.to_csv("{}/logs/trajectory.txt".format(self.root_dir), \
                       sep=' ', index=False, header=False)  
        # You can change the separator as needed
        return df, df_traj, initial_rows

    def load_n_save_baseline_estimated_traj(self, trajectory, trial):
        # Step 0: Read the CSV file
        df = pd.read_csv("{}/PythonAPI/Baselines/{}_{}.csv".format(self.root_dir, trajectory, trial))
        
        for index, value in enumerate(df['TimeStamp'][1:-1], start=1):
            if(value == df.at[index+1, 'TimeStamp'] or value == 0 or value < df.at[index-1, 'TimeStamp']):
                df.at[index, 'TimeStamp'] = 0.5*(df.at[index-1, 'TimeStamp'] + df.at[index+1, 'TimeStamp'])
        #assert(df["TimeStamp"].is_monotonic_increasing)
        #assert(df["TimeStamp"].is_unique)

        # Step 2: Drop the rows of initialization
        target = 2
        initial_rows = (df["TrackMode"] == target).idxmax()
        initial_rows += 2
        df = df.iloc[initial_rows:].reset_index(drop=True)

        # Step 3: Select several columns by their names
        df_traj = copy.deepcopy(df)
        selected_columns = ["TimeStamp","PX","PY","PZ","QX","QY","QZ","QW"]  # Replace with your desired column names
        df_traj = df_traj[selected_columns]

        # replace Nan with 0
        df_traj.fillna(0, inplace=True)

        # Step 4: Save the DataFrame as a text (TXT) file
        df_traj.to_csv("{}/logs/trajectory.txt".format(self.root_dir), \
                       sep=' ', index=False, header=False)  
        # You can change the separator as needed
        return df, df_traj, initial_rows

    def load_n_save_rl_estimated_traj(self, trajectory, trial):
        # Step 0: Read the CSV file
        df = pd.read_csv("{}/PythonAPI/RandomActions/{}_{}.csv".format(self.root_dir, trajectory, trial))
        
        for index, value in enumerate(df['TimeStamp'][1:-1], start=1):
            if(value == df.at[index+1, 'TimeStamp'] or value == 0 or value < df.at[index-1, 'TimeStamp']):
                df.at[index, 'TimeStamp'] = 0.5*(df.at[index-1, 'TimeStamp'] + df.at[index+1, 'TimeStamp'])
        #assert(df["TimeStamp"].is_monotonic_increasing)
        #assert(df["TimeStamp"].is_unique)

        # Step 2: Drop the rows of initialization
        target = 2
        initial_rows = (df["TrackMode"] == target).idxmax()
        initial_rows += 2
        df = df.iloc[initial_rows:].reset_index(drop=True)

        # Step 3: Select several columns by their names
        df_traj = copy.deepcopy(df)
        selected_columns = ["TimeStamp","PX","PY","PZ","QX","QY","QZ","QW"]  # Replace with your desired column names
        df_traj = df_traj[selected_columns]

        # replace Nan with 0
        df_traj.fillna(0, inplace=True)

        # Step 4: Save the DataFrame as a text (TXT) file
        df_traj.to_csv("{}/logs/trajectory.txt".format(self.root_dir), \
                       sep=' ', index=False, header=False)  
        # You can change the separator as needed
        return df, df_traj, initial_rows


class TUMRGBD1:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.benchmark = "TUMRGBD1"
        self.scriptTemplate = "{}/Examples/Monocular/mono_tum {}/Vocabulary/ORBvoc.txt {}/Examples/Monocular/TUM1.yaml {}/datasets/TUMRGBD1/{}/{}/"
        self.trajectories = [
            'rgbd_dataset_freiburg1_360',
            'rgbd_dataset_freiburg1_desk',
            'rgbd_dataset_freiburg1_desk2',
            'rgbd_dataset_freiburg1_floor',
            'rgbd_dataset_freiburg1_plant',
            'rgbd_dataset_freiburg1_room',
            'rgbd_dataset_freiburg1_rpy',
            'rgbd_dataset_freiburg1_teddy',
            'rgbd_dataset_freiburg1_xyz'
        ]
        self.scriptList = []

    def generate_script(self):
        self.scriptList = []
        for i, trajectory in enumerate(self.trajectories):
            scriptDict = {}
            scriptDict["benchmark"] = self.benchmark
            scriptDict["trajectory"] = trajectory
            scriptTemp = copy.deepcopy(self.scriptTemplate)
            scriptTemp = scriptTemp.format(self.root_dir, self.root_dir, self.root_dir, \
                                           self.root_dir, trajectory, trajectory)
            scriptDict["script"] = scriptTemp
            self.scriptList.append(scriptDict)

    def get_script(self):
        return self.scriptList

    def copy_ground_truth_traj(self, trajectory):
        gt_csv_path = "{}/datasets/TUMRGBD1/{}/{}/groundtruth.txt"
        gt_csv_path = gt_csv_path.format(self.root_dir, trajectory, trajectory)
        df = pd.read_csv(gt_csv_path, skiprows=3, \
                         header=None, delim_whitespace=True)
        df.to_csv("{}/logs/ground_truth.txt".format(self.root_dir), sep=' ', index=False, header=False)

    def load_n_save_estimated_traj(self):
        # Step 0: Read the CSV file
        df = pd.read_csv("{}/logs/log.csv".format(self.root_dir))
        
        # Step 1: Check duplicated time stamp
        for index, value in enumerate(df['TimeStamp'][1:-1], start=1):
            if(value == df.at[index+1, 'TimeStamp'] or value == 0 or value < df.at[index-1, 'TimeStamp']):
                df.at[index, 'TimeStamp'] = 0.5*(df.at[index-1, 'TimeStamp'] + df.at[index+1, 'TimeStamp'])
        #assert(df["TimeStamp"].is_monotonic_increasing)
        #assert(df["TimeStamp"].is_unique)

        # Step 2: Drop the rows of initialization
        target = 2
        initial_rows = (df["TrackMode"] == target).idxmax()
        initial_rows += 2
        df = df.iloc[initial_rows:].reset_index(drop=True)

        # Step 3: Select several columns by their names
        df_traj = copy.deepcopy(df)
        selected_columns = ["TimeStamp","PX","PY","PZ","QX","QY","QZ","QW"]  # Replace with your desired column names
        df_traj = df_traj[selected_columns]

        # Step 4: Save the DataFrame as a text (TXT) file
        df_traj.to_csv("{}/logs/trajectory.txt".format(self.root_dir), \
                       sep=' ', index=False, header=False)  
        # You can change the separator as needed
        return df, df_traj, initial_rows


class TUMRGBD2:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.benchmark = "TUMRGBD2"
        self.scriptTemplate = "{}/Examples/Monocular/mono_tum {}/Vocabulary/ORBvoc.txt {}/Examples/Monocular/TUM2.yaml {}/datasets/TUMRGBD2/{}/{}/"
        self.trajectories = [
            'rgbd_dataset_freiburg2_360_hemisphere',
            'rgbd_dataset_freiburg2_360_kidnap',
            'rgbd_dataset_freiburg2_coke',
            'rgbd_dataset_freiburg2_desk',
            'rgbd_dataset_freiburg2_desk_with_person',
            'rgbd_dataset_freiburg2_dishes',
            'rgbd_dataset_freiburg2_flowerbouquet',
            'rgbd_dataset_freiburg2_flowerbouquet_brownbackground',
            'rgbd_dataset_freiburg2_large_no_loop',
            'rgbd_dataset_freiburg2_large_with_loop',
            'rgbd_dataset_freiburg2_metallic_sphere',
            'rgbd_dataset_freiburg2_metallic_sphere2',
            'rgbd_dataset_freiburg2_pioneer_360',
            'rgbd_dataset_freiburg2_pioneer_slam',
            'rgbd_dataset_freiburg2_pioneer_slam2',
            'rgbd_dataset_freiburg2_pioneer_slam3',
            'rgbd_dataset_freiburg2_rpy',
            'rgbd_dataset_freiburg2_xyz'
        ]
        self.scriptList = []

    def generate_script(self):
        self.scriptList = []
        for i, trajectory in enumerate(self.trajectories):
            scriptDict = {}
            scriptDict["benchmark"] = self.benchmark
            scriptDict["trajectory"] = trajectory
            scriptTemp = copy.deepcopy(self.scriptTemplate)
            scriptTemp = scriptTemp.format(self.root_dir, self.root_dir, self.root_dir, \
                                           self.root_dir, trajectory, trajectory)
            scriptDict["script"] = scriptTemp
            self.scriptList.append(scriptDict)

    def get_script(self):
        return self.scriptList
    
    def copy_ground_truth_traj(self, trajectory):
        gt_csv_path = "{}/datasets/TUMRGBD2/{}/{}/groundtruth.txt"
        gt_csv_path = gt_csv_path.format(self.root_dir, trajectory, trajectory)
        df = pd.read_csv(gt_csv_path, skiprows=3, \
                         header=None, delim_whitespace=True)
        df.to_csv("{}/logs/ground_truth.txt".format(self.root_dir), sep=' ', index=False, header=False)

    def load_n_save_estimated_traj(self):
        # Step 0: Read the CSV file
        df = pd.read_csv("{}/logs/log.csv".format(self.root_dir))
        
        # Step 1: Check duplicated time stamp
        for index, value in enumerate(df['TimeStamp'][1:-1], start=1):
            if(value == df.at[index+1, 'TimeStamp'] or value == 0 or value < df.at[index-1, 'TimeStamp']):
                df.at[index, 'TimeStamp'] = 0.5*(df.at[index-1, 'TimeStamp'] + df.at[index+1, 'TimeStamp'])
        #assert(df["TimeStamp"].is_monotonic_increasing)
        #assert(df["TimeStamp"].is_unique)

        # Step 2: Drop the rows of initialization
        target = 2
        initial_rows = (df["TrackMode"] == target).idxmax()
        initial_rows += 2
        df = df.iloc[initial_rows:].reset_index(drop=True)

        # Step 3: Select several columns by their names
        df_traj = copy.deepcopy(df)
        selected_columns = ["TimeStamp","PX","PY","PZ","QX","QY","QZ","QW"]  # Replace with your desired column names
        df_traj = df_traj[selected_columns]

        # Step 4: Save the DataFrame as a text (TXT) file
        df_traj.to_csv("{}/logs/trajectory.txt".format(self.root_dir), \
                       sep=' ', index=False, header=False)  
        # You can change the separator as needed
        return df, df_traj, initial_rows

class TUMRGBD3:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.benchmark = "TUMRGBD3"
        self.scriptTemplate = "{}/Examples/Monocular/mono_tum {}/Vocabulary/ORBvoc.txt {}/Examples/Monocular/TUM3.yaml {}/datasets/TUMRGBD3/{}/{}/"
        self.trajectories = [
            'rgbd_dataset_freiburg3_cabinet',
            'rgbd_dataset_freiburg3_large_cabinet',
            'rgbd_dataset_freiburg3_long_office_household',
            'rgbd_dataset_freiburg3_nostructure_notexture_far',
            'rgbd_dataset_freiburg3_nostructure_notexture_near_withloop',
            'rgbd_dataset_freiburg3_nostructure_texture_far',
            'rgbd_dataset_freiburg3_nostructure_texture_near_withloop',
            'rgbd_dataset_freiburg3_sitting_halfsphere',
            'rgbd_dataset_freiburg3_sitting_rpy',
            'rgbd_dataset_freiburg3_sitting_static',
            'rgbd_dataset_freiburg3_sitting_xyz',
            'rgbd_dataset_freiburg3_structure_notexture_far',
            'rgbd_dataset_freiburg3_structure_notexture_near',
            'rgbd_dataset_freiburg3_structure_texture_far',
            'rgbd_dataset_freiburg3_structure_texture_near',
            'rgbd_dataset_freiburg3_teddy',
            'rgbd_dataset_freiburg3_walking_halfsphere',
            'rgbd_dataset_freiburg3_walking_rpy',
            'rgbd_dataset_freiburg3_walking_static',
            'rgbd_dataset_freiburg3_walking_xyz'
        ]
        self.scriptList = []

    def generate_script(self):
        self.scriptList = []
        for i, trajectory in enumerate(self.trajectories):
            scriptDict = {}
            scriptDict["benchmark"] = self.benchmark
            scriptDict["trajectory"] = trajectory
            scriptTemp = copy.deepcopy(self.scriptTemplate)
            scriptTemp = scriptTemp.format(self.root_dir, self.root_dir, self.root_dir, \
                                           self.root_dir, trajectory, trajectory)
            scriptDict["script"] = scriptTemp
            self.scriptList.append(scriptDict)

    def get_script(self):
        return self.scriptList
    
    def copy_ground_truth_traj(self, trajectory):
        gt_csv_path = "{}/datasets/TUMRGBD3/{}/{}/groundtruth.txt"
        gt_csv_path = gt_csv_path.format(self.root_dir, trajectory, trajectory)
        df = pd.read_csv(gt_csv_path, skiprows=3, \
                         header=None, delim_whitespace=True)
        df.to_csv("{}/logs/ground_truth.txt".format(self.root_dir), sep=' ', index=False, header=False)

    def load_n_save_estimated_traj(self):
        # Step 0: Read the CSV file
        df = pd.read_csv("{}/logs/log.csv".format(self.root_dir))
        
        # Step 1: Check duplicated time stamp
        for index, value in enumerate(df['TimeStamp'][1:-1], start=1):
            if(value == df.at[index+1, 'TimeStamp'] or value == 0 or value < df.at[index-1, 'TimeStamp']):
                df.at[index, 'TimeStamp'] = 0.5*(df.at[index-1, 'TimeStamp'] + df.at[index+1, 'TimeStamp'])
        #assert(df["TimeStamp"].is_monotonic_increasing)
        #assert(df["TimeStamp"].is_unique)

        # Step 2: Drop the rows of initialization
        target = 2
        initial_rows = (df["TrackMode"] == target).idxmax()
        initial_rows += 2
        df = df.iloc[initial_rows:].reset_index(drop=True)

        # Step 3: Select several columns by their names
        df_traj = copy.deepcopy(df)
        selected_columns = ["TimeStamp","PX","PY","PZ","QX","QY","QZ","QW"]  # Replace with your desired column names
        df_traj = df_traj[selected_columns]

        # Step 4: Save the DataFrame as a text (TXT) file
        df_traj.to_csv("{}/logs/trajectory.txt".format(self.root_dir), \
                       sep=' ', index=False, header=False)  
        # You can change the separator as needed
        return df, df_traj, initial_rows


benchmark_factory = {
    "SenseTime": SenseTime,
    "TUMRGBD1": TUMRGBD1,
    "TUMRGBD2": TUMRGBD2,
    "TUMRGBD3": TUMRGBD3,
    "Unity": Unity
}
