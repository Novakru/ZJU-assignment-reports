"""Q1.3: sequence-first, four-layer RNN."""
import torch
from torch import nn

torch.manual_seed(1050)
torch.set_num_threads(2)
x = torch.randn(28, 20, 96)
rnn = nn.RNN(96, 192, num_layers=4)
h0 = torch.randn(4, 20, 192)
with torch.no_grad():
    output, hn = rnn(x, h0)
assert output.shape == (28, 20, 192)
assert hn.shape == (4, 20, 192)
print("Output:", tuple(output.shape))
print("Final hidden state:", tuple(hn.shape))
