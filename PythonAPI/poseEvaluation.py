from evo.tools import log
log.configure_logging(verbose=True, debug=True, silent=False)

import pprint
import numpy as np

from evo.tools import plot
import matplotlib.pyplot as plt
# %matplotlib inline
# %matplotlib notebook

# temporarily override some package settings
from evo.tools.settings import SETTINGS
SETTINGS.plot_usetex = False

from evo.tools import file_interface
from evo.core import sync
from evo.core import metrics

# Import for plotting trajectory with error magnitude
from evo.core.metrics import PoseRelation, Unit

import copy
import pandas as pd

# Import for regional alignment
from evo import core
from evo.core.trajectory import PosePath3D, PoseTrajectory3D

class PoseErrorEvaluator:
    def __init__(self, root_dir, delta=60, max_diff=0.05, max_null_length=10):
        self.root_dir = root_dir
        self.delta = delta
        self.max_diff = max_diff
        self.max_null_length = max_null_length
        self.traj_ref = None
        self.traj_est = None
        self.merged_df = None       

    def load_trajectory(self):
        ref_file = "{}/logs/ground_truth.txt".format(self.root_dir)
        est_file = "{}/logs/trajectory.txt".format(self.root_dir)

        traj_est = file_interface.read_tum_trajectory_file(est_file)
        traj_ref = file_interface.read_tum_trajectory_file(ref_file)

        # Just in case that
        # the first timestamp is not initialized yet
        traj_est.timestamps[0] = traj_est.timestamps[1] - 0.03

        align_regions = []
        shifts = np.where(traj_est.speeds>5)[0]
        if shifts is not None:
            # generate align regions
            shifts_idx = [0] + [x for x in shifts] + [traj_est.num_poses]
            for idx in range(len(shifts_idx[0:-1])):
                align_regions.append([shifts_idx[idx],shifts_idx[idx+1]])
                
            print("Subtrajectories for alignment: {}".format(align_regions))
            # split trajectory to subtrajectories
            xyz = traj_est._positions_xyz
            quat = traj_est._orientations_quat_wxyz
            time = traj_est.timestamps
            subtrajectories = []
            for region in align_regions:
                xyz_sub = xyz[region[0]:region[1], :]
                xyz_sub[0,:] = xyz_sub[1,:]
                xyz_sub[-1,:] = xyz_sub[-2,:]
                
                quat_sub = quat[region[0]:region[1], :]
                quat_sub[0,:] = quat_sub[1,:]
                quat_sub[-1,:] = quat_sub[-2,:]

                time_sub = time[region[0]:region[1]]
                traj_sub = PoseTrajectory3D(xyz_sub, quat_sub, time_sub)
                print("Original estimated subtrajectory length: {}".format(traj_sub.num_poses))
                try:
                    traj_ref_copy = copy.deepcopy(traj_ref)
                    traj_ref_copy, traj_sub = sync.associate_trajectories(traj_ref_copy, traj_sub, max_diff=0.05)
                    
                    #n = int(traj_sub.timestamps.shape[0]/2)
                    #traj_sub.align(traj_ref_copy, correct_scale=True, correct_only_scale=False, n=n)
                    traj_sub.align(traj_ref_copy, correct_scale=True, correct_only_scale=False)
                    
                    subtrajectories.append(traj_sub)
                    
                    #self.plot_trajectory(traj_sub, traj_ref)
                except:
                    print("subtrajectory alignment failed")

                #print("="*50)
            traj_est_aligned = core.trajectory.merge(subtrajectories)
            traj_ref, traj_est_aligned = sync.associate_trajectories(traj_ref, traj_est_aligned, self.max_diff)
            #n = int(traj_est_aligned.timestamps.shape[0]/2)
            #print("aligned length: {}".format(n))
            #traj_est_aligned.align(traj_ref, correct_scale=True, correct_only_scale=False, n=n)


        else:
            print("Original estimated trajectory length: {}".format(traj_ref.num_poses))
            
            traj_ref, traj_est = sync.associate_trajectories(traj_ref, traj_est, self.max_diff)

            # trajectory length might change if the ground truth is missing/ cannot synchronized
            print("Synchronized estimated trajectory length: {}".format(traj_ref.num_poses))
                    
            traj_est_aligned = copy.deepcopy(traj_est)
            #traj_est_aligned.align(traj_ref, correct_scale=True, correct_only_scale=False)
            n = int(traj_est_aligned.timestamps.shape[0]/2)
            print("aligned length: {}".format(n))
            traj_est_aligned.align(traj_ref, correct_scale=True, correct_only_scale=False, n=n)


        self.traj_ref = traj_ref
        #self.traj_est = traj_est
        self.traj_est = traj_est_aligned
        print("Loaded trajectory ({} poses)  with ground truth {} poses".format(traj_est_aligned.num_poses, traj_ref.num_poses))
        print("="*50)

    def calculate_RE(self, pose_relation = metrics.PoseRelation.translation_part):
        # error metric settings
        #pose_relation = metrics.PoseRelation.translation_part
        #pose_relation = metrics.PoseRelation.point_distance
        #pose_relation = metrics.PoseRelation.point_distance_error_ratio
        
        delta_unit = metrics.Unit.frames
        all_pairs = True
        # form the (reference, estimation) pair
        data = (self.traj_ref, self.traj_est)
        # load error metric setting
        rpe_metric = metrics.RPE(pose_relation=pose_relation, delta=self.delta,
                                delta_unit=delta_unit, all_pairs=all_pairs)
        # calculate the error
        rpe_metric.process_data(data)
        # devided by the subjectory length --> invariant to the length
        error = np.array(rpe_metric.error)#/float(self.delta) 

        # assign time stamps to the error
        timeStamps = self.traj_ref.timestamps[self.delta:]
        assert(len(timeStamps==len(error)))
        self.error_df = pd.DataFrame({'TimeStamp': timeStamps, 'RelativeError': error})
        print("Loaded trajectory with ground truth")
        print("="*50)
        return rpe_metric

    # Interpolate consecutive null values up to max_null_length
    @staticmethod
    def interpolate_consecutive_nulls(column_df, max_null_length=10):
        column = copy.deepcopy(column_df)
        is_null = column.isnull()
        consecutive_nulls = 0
        for i in range(len(column)):
            if is_null[i]:
                consecutive_nulls += 1
            else:
                # igonre long null sequence
                if consecutive_nulls >= max_null_length:
                    consecutive_nulls = 0
                elif consecutive_nulls > 0:
                    # Interpolate using linear method for consecutive null values
                    column[i - consecutive_nulls:i] = np.linspace(column[i - consecutive_nulls - 1], column[i], consecutive_nulls + 2)[1:-1]
                consecutive_nulls = 0
        return column


    def merge_feature_with_label(self, trajectory, trial=None):
        # load feature
        if trial is not None:
            feature_df = pd.read_csv("{}/PythonAPI/RandomActions/{}_{}.csv".format(self.root_dir, trajectory, trial))
        else:
            feature_df = pd.read_csv("{}/PythonAPI/Baselines/{}.csv".format(self.root_dir, trajectory))

        # Step 1: Check duplicated/zero time stamp
        for index, value in enumerate(feature_df['TimeStamp'][1:-1], start=1):
            if(value == feature_df.at[index+1, 'TimeStamp'] or value == 0 or value < feature_df.at[index-1, 'TimeStamp']):
                feature_df.at[index, 'TimeStamp'] = 0.5*(feature_df.at[index-1, 'TimeStamp'] + feature_df.at[index+1, 'TimeStamp'])
        #assert(feature_df["TimeStamp"].is_monotonic_increasing)
        #assert(feature_df["TimeStamp"].is_unique)

        error_df = self.error_df
        # merge feature
        merged_df = pd.merge_asof(feature_df, error_df , on='TimeStamp', tolerance=self.max_diff)
        # move label to the front
        # Column to move to the first position
        column_to_move = 'RelativeError'
        # Reorder the columns
        new_columns = [column_to_move] + [col for col in merged_df.columns if col != column_to_move]
        merged_df = merged_df[new_columns]
        merged_df["RelativeError"] = PoseErrorEvaluator.interpolate_consecutive_nulls(merged_df["RelativeError"], 
                                                                                      self.max_null_length)
        self.merged_df = merged_df


    def calculate_reward(self, trajectory, trial):
        # load feature
        rl_df = pd.read_csv("{}/data/RL_SenseTime_{}_{}.csv".format(self.root_dir, trajectory, trial))
        baseline_df = pd.read_csv("{}/data/baseline_SenseTime_{}_{}.csv".format(self.root_dir, trajectory, trial))

        baseline_df.loc[baseline_df['TrackMode'] == 3, 'RelativeError'] = 10
        rl_df.loc[rl_df['TrackMode'] == 3, 'RelativeError'] = 10

        baseline_error_df = baseline_df[["TimeStamp", "RelativeError"]]
        # Rename the 'OldColumn' to 'NewColumn'
        baseline_error_df.rename(columns={'RelativeError': 'BaseRelativeError'}, inplace=True)
        
        combined_df = pd.merge_asof(rl_df, baseline_error_df , on='TimeStamp', tolerance=self.max_diff)
        column_to_move = 'BaseRelativeError'
        # Reorder the columns
        new_columns = [column_to_move] + [col for col in combined_df.columns if col != column_to_move]
        combined_df = combined_df[new_columns]
        combined_df['RelativeError'].fillna(10, inplace=True)
        combined_df['BaseRelativeError'].fillna(10, inplace=True)

        # Calculate the difference between Column1 and Column2 and save it in a new column 'Difference'
        combined_df['Reward'] = combined_df['BaseRelativeError'] - combined_df['RelativeError']
        column_to_move = 'Reward'
        # Reorder the columns
        new_columns = [column_to_move] + [col for col in combined_df.columns if col != column_to_move]
        combined_df = combined_df[new_columns]

        return combined_df


    def get_traj_w_gt(self):
        return self.traj_est, self.traj_ref

    def get_feature_w_label(self):
        return self.merged_df
    
    def get_error_df(self):
        return self.error_df

    @staticmethod
    def attach_label_2_features(delta, error, df):
        new_column_name = 'RelativeError'
        df_label = pd.DataFrame({new_column_name: error})
        df = df.iloc[delta:].reset_index(drop=True)
        if(len(df) != len(df_label)):
            print(len(df))
            print(len(df_label))
            diff = len(df) - len(df_label)
            df = df.iloc[diff:]
            assert(diff <= 30)
        data_df = pd.concat([df_label, df], ignore_index=True, axis=1)
        return data_df

    @staticmethod
    def plot_aligned_trajectory(traj_est, traj_ref, benchmark=None, trajectory=None, trial=None, mode=None):
        fig = plt.figure(figsize=[10,10])
        
        traj_est_aligned = copy.deepcopy(traj_est)
        traj_est_aligned.align(traj_ref, correct_scale=True, correct_only_scale=False)
        
        traj_by_label = {
            #"estimate (not aligned)": traj_est,
            "estimate (aligned)": traj_est_aligned,
            "reference": traj_ref
        }
        
        plot.trajectories(fig, traj_by_label, plot.PlotMode.xyz)
        fig.savefig('./figures/{}-{}-{}-{}-trajectory.png'.format(benchmark, trajectory, trial, mode))

    @staticmethod
    def plot_error(error_df, delta, benchmark=None, trajectory=None, trial=None, mode=None):
        fig = plt.figure(figsize=[10,3])
        # Plot the line
        plt.plot(error_df['TimeStamp'], error_df['RelativeError'])
        plt.ylim(-0.05, 2.0)
        # Add labels and title
        plt.xlabel('Time Step')
        plt.ylabel('Relative Error')
        plt.title('Relative Error on {}-{}-{} with sub-trajectory={} frames'.format(benchmark, 
                                                                                        trajectory, 
                                                                                        trial, 
                                                                                        delta))

        fig.savefig('./figures/{}-{}-{}-{}-error.png'.format(benchmark, trajectory, trial, mode))

    @staticmethod
    def plot_trajectory_with_error(rpe_metric, traj_ref, traj_est_aligned, benchmark, trajectory, trial, mode=None):
        result = rpe_metric.get_result()
        
        plot_mode = plot.PlotMode(plot.PlotMode.xy)
        # Plot the values color-mapped onto the trajectory.
        fig = plt.figure(figsize=(10,10))
        ax = plot.prepare_axis(
            fig, plot_mode,
            length_unit=Unit(SETTINGS.plot_trajectory_length_unit))
        plot.traj(ax, plot_mode, traj_ref,
              style=SETTINGS.plot_reference_linestyle,
              color=SETTINGS.plot_reference_color, label='reference',
              alpha=SETTINGS.plot_reference_alpha,
              plot_start_end_markers=SETTINGS.plot_start_end_markers)
        plot.draw_coordinate_axes(ax, traj_ref, plot_mode,
                              SETTINGS.plot_reference_axis_marker_scale)
    
        plot_colormap_min = result.stats["min"]
        plot_colormap_max = result.stats["max"]
        plot_colormap_max = np.percentile(
            result.np_arrays["error_array"], 100)               

        plot.traj_colormap(ax, traj_est_aligned, result.np_arrays["error_array"],
                       plot_mode, min_map=plot_colormap_min,
                       max_map=plot_colormap_max,
                       title=result.info["title"],
                       plot_start_end_markers=SETTINGS.plot_start_end_markers)

        plot.draw_coordinate_axes(ax, traj_est_aligned, plot_mode,
                                SETTINGS.plot_axis_marker_scale)
        fig.savefig('./figures/{}-{}-{}-{}-trajectory-error.png'.format(benchmark, trajectory, trial, mode))

