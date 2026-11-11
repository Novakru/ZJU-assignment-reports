"""Q2: exact normalization and all matrix intermediates."""
import sympy as sp

A = sp.ones(3) - sp.eye(3)
X = sp.Matrix([[1, 2], [2, 1], [0, 1]])
W = sp.Matrix([[2, 1], [0, 1]])
A_tilde = A + sp.eye(3)
D = sp.diag(*[sum(A_tilde.row(i)) for i in range(3)])
D_inv_sqrt = D.applyfunc(
    lambda value: 1 / sp.sqrt(value) if value else 0)
normalized = D_inv_sqrt * A_tilde * D_inv_sqrt
H = normalized * X * W
assert H == sp.Matrix([[2, sp.Rational(7, 3)]] * 3)
for name, value in [
    ("A + I", A_tilde), ("D", D),
    ("D^(-1/2)", D_inv_sqrt), ("Normalized adjacency", normalized),
    ("X W", X * W), ("H^(1)", H),
]:
    print(name + ":")
    print(value)
