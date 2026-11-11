"""Q1.1: change only the last feature dimension."""
import torch
from torch import nn

torch.manual_seed(1050)
x = torch.randn(80, 640)
m = nn.Linear(640, 320)
with torch.no_grad():
    output = m(x)
assert output.shape == (80, 320)
print("Output:", tuple(output.shape))
