"""Q3: one bilinear sample, illustrating fractional coordinates."""
import numpy as np

feature = np.array([[0., 10.], [20., 30.]])
x, y = 0.25, 0.5
sample = ((1 - x) * (1 - y) * feature[0, 0]
          + x * (1 - y) * feature[0, 1]
          + (1 - x) * y * feature[1, 0]
          + x * y * feature[1, 1])
assert np.isclose(sample, 12.5)
print("Fractional sample coordinate (x, y):", (x, y))
print("Bilinear feature value:", sample)
print("Illustration of one sample, not a full ROI Align layer.")
