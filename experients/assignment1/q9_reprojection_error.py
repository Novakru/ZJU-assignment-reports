"""Q9: use exact homogeneous projection and Euclidean pixel error."""
import sympy as sp


def reprojection_error():
    P = sp.Matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]])
    world = sp.Matrix([3, 1, 2, 1])
    measured = sp.Matrix([280, 200])
    image_h = P * world
    projected = image_h[:2, 0] / image_h[2]
    residual = projected - measured
    squared = residual.dot(residual)
    return projected, residual, squared, sp.sqrt(squared)


if __name__ == "__main__":
    projected, residual, squared, error = reprojection_error()
    print("Projected image point:", tuple(projected))
    print("Residual (predicted - measured):", tuple(residual))
    print("Squared error (px^2):", squared)
    print(f"Euclidean reprojection error (px): {float(error):.10f}")
