"""Q1: compute both vanishing points as exact symbolic limits."""
import sympy as sp


def vanishing_points():
    lam = sp.symbols("lambda", positive=True)
    direction = sp.Matrix([4, 2, 5])
    origins = (sp.Matrix([3, 1, 6]), sp.Matrix([7, 4, 2]))
    points = []
    for origin in origins:
        point = origin + lam * direction
        points.append(tuple(sp.limit(point[j] / point[2], lam, sp.oo)
                            for j in (0, 1)))
    return points


if __name__ == "__main__":
    q, r = vanishing_points()
    print("Q vanishing point:", q)
    print("R vanishing point:", r)
    print("Same vanishing point:", q == r)
