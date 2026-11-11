"""Q1.4: batch-first encoder with six attention heads."""
import torch
from torch import nn

torch.manual_seed(1050)
torch.set_num_threads(2)
x = torch.rand(80, 24, 384)
encoder_layer = nn.TransformerEncoderLayer(
    d_model=384, nhead=6, batch_first=True)
encoder_layer.eval()
with torch.no_grad():
    out = encoder_layer(x)
assert out.shape == (80, 24, 384)
print("Output:", tuple(out.shape))
print("Features per head:", 384 // 6)
