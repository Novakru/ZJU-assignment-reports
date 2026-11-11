"""Q4: parameter layout of the common 10-shape SMPL setting."""
import numpy as np

theta = np.zeros((24, 3))
beta = np.zeros(10)
assert theta.size == 72
print("Pose: 24 axis-angle rotations:", theta.shape)
print("Pose scalar count:", theta.size)
print("Shape coefficient count (common setting):", beta.size)
