"""Q4: symbolically verify distance preservation for an orthogonal R."""
import sympy as sp


def distance_check():
    R = sp.MatrixSymbol("R", 3, 3)
    x, y = (sp.MatrixSymbol(name, 3, 1) for name in ("x", "y"))
    t = sp.Matrix([-3, 2, 1])
    difference = (R * x + t) - (R * y + t)
    cancellation = (difference - R * (x - y)).as_explicit()
    cancels = cancellation.applyfunc(sp.simplify) == sp.zeros(3, 1)
    # Orthogonality is the given rotation-matrix assumption.
    gram = sp.refine(R.T * R, sp.Q.orthogonal(R)).doit()
    d = sp.MatrixSymbol("d", 3, 1)
    change = (d.T * (gram.as_explicit() - sp.eye(3)) * d)[0, 0]
    return cancels, gram, sp.simplify(change)


if __name__ == "__main__":
    cancels, gram, change = distance_check()
    print("The common translation cancels:", cancels)
    print("R.T * R for a rotation matrix:", gram)
    print("Change in squared distance:", change)
    print("Euclidean distances are equal:", cancels and change == 0)
