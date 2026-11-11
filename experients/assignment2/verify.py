"""Additional checks: independent algebra and network gradient flow."""
from fractions import Fraction
import sympy as sp
import torch
from q1_5_network import SequenceNetwork

torch.manual_seed(1050)
torch.set_num_threads(2)
model = SequenceNetwork()
x = torch.randn(2, 5, 384, requires_grad=True)
y = model(x)
y.square().mean().backward()
for name, module in [("Linear", model.linear), ("Conv1d", model.conv),
                     ("Transformer", model.encoder), ("RNN", model.rnn)]:
    grads = [p.grad for p in module.parameters()]
    assert all(g is not None and torch.isfinite(g).all() for g in grads)
    assert any(g.abs().sum() > 0 for g in grads)
    print("PASS: gradient flows through", name)
assert x.grad is not None and torch.isfinite(x.grad).all()
X = sp.Matrix([[1, 2], [2, 1], [0, 1]])
W = sp.Matrix([[2, 1], [0, 1]])
mean_then_transform = sp.ones(3, 1) * (
    sp.ones(1, 3) * X / 3) * W
assert mean_then_transform == sp.Matrix([[2, sp.Rational(7, 3)]] * 3)
print("PASS: GCN via mean first, then feature transform")
P = sp.Matrix([[0, 1], [0, 0]])
values = (sp.eye(2) - sp.Rational(4, 5) * P).inv() * sp.Matrix([-3, 12])
assert values == sp.Matrix([sp.Rational(33, 5), 12])
print("PASS: Bellman linear system gives V(A)=33/5, V(B)=12")
print("All additional checks passed.")
