"""Q1.5: Linear -> Conv1d -> Transformer -> RNN."""
import torch
from torch import nn


class SequenceNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(384, 384)
        self.conv = nn.Conv1d(384, 384, kernel_size=3, padding=1)
        self.encoder = nn.TransformerEncoderLayer(
            d_model=384, nhead=6, batch_first=True)
        self.rnn = nn.RNN(384, 384, batch_first=True)

    def forward(self, x):
        x = self.linear(x)
        x = self.conv(x.transpose(1, 2)).transpose(1, 2)
        x = self.encoder(x)
        x, _ = self.rnn(x)
        return x


if __name__ == "__main__":
    torch.manual_seed(1050)
    torch.set_num_threads(2)
    model = SequenceNetwork().eval()
    x = torch.randn(64, 24, 384)
    with torch.no_grad():
        output = model(x)
    assert output.shape == x.shape
    assert torch.isfinite(output).all()
    print("Input:", tuple(x.shape))
    print("Output:", tuple(output.shape))
