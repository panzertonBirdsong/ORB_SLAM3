import numpy as np
from collections import deque
import math

class StreamingAPE:
    def __init__(self, gt_path, n_traj=50):

        self.n_traj   = n_traj

        self.gt_ts, self.gt_pos = self._read_gt(gt_path)

        self.aligned = False
        self.s = 1.0
        self.R = np.eye(3)
        self.t = np.zeros(3)

        self._est_pts = []
        self._gt_pts  = []

        self.n = 0
        self.sum_sq = 0.0
        self.rmse = 0.0

    def add_pose(self, est_sample):
        self.n += 1
        t_e = est_sample[0]
        p_e = np.array(est_sample[1:4], dtype=float)

        p_g = self._interp_gt_pos(t_e)
        if p_g is None:
            return None, None

        self._est_pts.append(p_e)
        self._gt_pts.append(p_g)
        
        
        if len(self._est_pts) >= self.n_traj and self.n % 100 == 0 and self.n != 0:
            self._build_alignment()

        if not self.aligned:
            return None, None
        
        p_e_aligned = self.s * (self.R @ p_e) + self.t

        e = np.linalg.norm(p_g - p_e_aligned)

        self.sum_sq += e**2
        self.rmse = math.sqrt(self.sum_sq / self.n)

        return e, self.rmse

    def _read_gt(self, path):
        ts = []
        pos = []
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.replace(',', ' ').split()
                if len(parts) < 8:
                    continue
                t = float(parts[0])
                px, py, pz = map(float, parts[1:4])
                ts.append(t)
                pos.append([px, py, pz])
        ts  = np.array(ts)
        pos = np.array(pos)

        order = np.argsort(ts)
        return ts[order], pos[order]

    def _interp_gt_pos(self, t):
        ts = self.gt_ts
        if t < ts[0] or t > ts[-1]:
            return None
        idx = np.searchsorted(ts, t)
        if idx == 0:
            return self.gt_pos[0]
        if idx == len(ts):
            return self.gt_pos[-1]
        t0, t1 = ts[idx-1], ts[idx]
        p0, p1 = self.gt_pos[idx-1], self.gt_pos[idx]
        alpha = (t - t0) / (t1 - t0)
        return (1 - alpha) * p0 + alpha * p1

    def _build_alignment(self):
        X = np.array(self._est_pts)
        Y = np.array(self._gt_pts)
        self.s, self.R, self.t = self._umeyama(X, Y)
        self.aligned = True
        self._est_pts.clear(); self._gt_pts.clear()

    @staticmethod
    def _umeyama(X, Y):
        muX, muY = X.mean(0), Y.mean(0)
        Xc, Yc = X - muX, Y - muY
        Cov = (Xc.T @ Yc) / X.shape[0]
        U, D, Vt = np.linalg.svd(Cov)
        R = U @ np.diag([1, 1, np.sign(np.linalg.det(U @ Vt))]) @ Vt
        varX = (Xc**2).sum()/X.shape[0]
        s = np.trace(np.diag(D)) / varX
        t = muY - s * (R @ muX)
        return s, R, t


