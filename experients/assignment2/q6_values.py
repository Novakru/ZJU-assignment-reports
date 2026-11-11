"""Q6: exact Bellman values and an independent return check."""
from fractions import Fraction

gamma = Fraction(4, 5)
V_D = Fraction(0)
V_B = 12 + gamma * V_D
V_A = -3 + gamma * V_B
assert V_A == -3 + gamma * 12
assert V_A == Fraction(33, 5) and V_B == 12
for state, value in [("D", V_D), ("B", V_B), ("A", V_A)]:
    print(f"V({state}) = {value} = {float(value):.1f}")
