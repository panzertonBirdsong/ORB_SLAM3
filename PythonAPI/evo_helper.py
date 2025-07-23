import itertools
import subprocess
import pathlib
import csv
import copy
import os
import time
from ruamel.yaml import YAML
from tqdm import tqdm




import sys
import os
from evo.core import metrics
from evo.core.units import Unit
from evo.tools import log
log.configure_logging(verbose=True, debug=True, silent=False)
import pprint
import numpy as np
from evo.tools import plot
import matplotlib.pyplot as plt
from evo.tools.settings import SETTINGS
SETTINGS.plot_usetex = False
plot.apply_settings(SETTINGS)
from evo.tools import file_interface
from evo.core import sync
import copy
import subprocess as sp
import csv
from pathlib import Path
import shutil




def evo_eval(eval_name, ref_file, est_file):

    os.makedirs(f"./orb_runs/{eval_name}", exist_ok=True)

    # ref_trimmed_file = ref_file.replace(".csv", "_trimmed.csv")
    ref_trimmed_file = Path(str(ref_file).replace(".csv", "_trimmed.csv"))

    with open(ref_file, "r") as infile, open(ref_trimmed_file, "w") as outfile:
        reader = csv.reader(infile)
        next(reader)  # skip header

        for row in reader:
            trimmed = row[:8]
            if len(trimmed) == 8 and all(cell.strip() != '' for cell in trimmed):
                line = " ".join(cell.strip() for cell in trimmed)
                outfile.write(line + "\n")



    traj_ref = file_interface.read_tum_trajectory_file(ref_trimmed_file)
    traj_est = file_interface.read_tum_trajectory_file(est_file)

    max_diff = 0.01
    try:
        traj_ref, traj_est = sync.associate_trajectories(traj_ref, traj_est, max_diff)
    except Exception:
        return 0

        
    traj_est_aligned = copy.deepcopy(traj_est)
    traj_est_aligned.align(traj_ref, correct_scale=False, correct_only_scale=False)


    # APE
    pose_relation = metrics.PoseRelation.translation_part
    use_aligned_trajectories = True
    if use_aligned_trajectories:
        data = (traj_ref, traj_est_aligned) 
    else:
        data = (traj_ref, traj_est)

    ape_metric = metrics.APE(pose_relation)
    ape_metric.process_data(data)

    ape_stat = ape_metric.get_statistic(metrics.StatisticsType.rmse)
    shutil.rmtree(f"./orb_runs/{eval_name}", ignore_errors=True)
    return ape_stat