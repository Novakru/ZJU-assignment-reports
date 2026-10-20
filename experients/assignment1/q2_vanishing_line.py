"""Q2: obtain the vanishing line from the plane normal."""
import sympy as sp


def vanishing_line():
    X, Y, Z, x, y = sp.symbols("X Y Z x y")
    plane = 6 * X + 3 * Y + 2 * Z - 17
    normal = sp.Matrix([sp.diff(plane, v) for v in (X, Y, Z)])
    line = sp.Eq(normal.dot(sp.Matrix([x, y, 1])), 0)
    return normal, line


if __name__ == "__main__":
    normal, line = vanishing_line()
    print("Plane normal:", tuple(normal))
    print("Vanishing line:", line)
    print("Homogeneous line coefficients:", tuple(normal))
