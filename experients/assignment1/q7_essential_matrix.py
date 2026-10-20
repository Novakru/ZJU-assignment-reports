"""Q7: E = [t]_cross R for the convention X2 = R X1 + t."""
import sympy as sp


def essential_matrix():
    R = sp.eye(3)
    tx, ty, tz = sp.Matrix([3, 0, 0])
    skew = sp.Matrix([[0, -tz, ty], [tz, 0, -tx], [-ty, tx, 0]])
    return skew * R


if __name__ == "__main__":
    E = essential_matrix()
    print("Essential matrix E:")
    for row in E.tolist():
        print(row)
    print("Rank:", E.rank())
