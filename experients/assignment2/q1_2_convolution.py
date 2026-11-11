"""Q1.2: actual CPU convolutions with the supplied input."""
import torch
from torch import nn

torch.manual_seed(1050)
torch.set_num_threads(2)
x = torch.randn(20, 36, 224, 160)
layers = [
    nn.Conv2d(36, 48, 3, stride=2),
    nn.Conv2d(36, 72, 4, stride=(2, 1), padding=(1, 2)),
    nn.Conv2d(36, 72, (5, 3), stride=(2, 3),
              padding=(2, 1), dilation=(1, 2), groups=6),
]
expected = [(20, 48, 111, 79), (20, 72, 112, 161),
            (20, 72, 112, 53)]
for label, layer, shape in zip("abc", layers, expected):
    with torch.no_grad():
        output = layer(x)
    assert tuple(output.shape) == shape
    print(f"({label}) Output:", tuple(output.shape))
