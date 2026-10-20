"""Q8: compute the corresponding epipolar line in image 2."""
import sympy as sp


def epipolar_line():
    tx, ty, tz = sp.Matrix([3, 0, 0])
    R = sp.eye(3)
    skew = sp.Matrix([[0, -tz, ty], [tz, 0, -tx], [-ty, tx, 0]])
    E = skew * R
    point = sp.Matrix([280, 200, 1])
    return E, E * point


if __name__ == "__main__":
    E, line = epipolar_line()
    y2 = sp.symbols("y2")
    print("Line coefficients E * p1:", tuple(line))
    print("Equivalent coefficients:", tuple(line / line[1]))
    print("Line equation:", sp.Eq(y2, sp.solve(line[1] * y2 + line[2], y2)[0]))
