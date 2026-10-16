"""Independent exact/numerical checks of the report's ten answers."""

import numpy as np
import sympy as sp

from q5_camera import IMAGE, WORLD, estimate_camera
from q6_triangulation import P1, P2, triangulate


def check(condition, message):
    if not condition:
        raise AssertionError(message)
    print(f"PASS: {message}")


def main():
    lam = sp.symbols("lambda", positive=True)
    direction = sp.Matrix([4, 2, 5])
    for origin in (sp.Matrix([3, 1, 6]), sp.Matrix([7, 4, 2])):
        point = origin + lam * direction
        limit = [sp.limit(point[i] / point[2], lam, sp.oo) for i in (0, 1)]
        check(limit == [sp.Rational(4, 5), sp.Rational(2, 5)],
              "Q1: parallel line has vanishing point (4/5, 2/5)")

    normal = sp.Matrix([6, 3, 2])
    tangent1, tangent2 = sp.Matrix([1, -2, 0]), sp.Matrix([0, 2, -3])
    check(normal.dot(tangent1) == normal.dot(tangent2) == 0
          and tangent1.cross(tangent2) == normal,
          "Q2: independent plane directions give line (6, 3, 2)")
    check(sp.Matrix([12, 8, 28]) == 4 * sp.Matrix([3, 2, 7]),
          "Q3: the plane normal equals four times the given vector")

    # Fixed seed; proper rotations constructed independently by QR.
    rng = np.random.default_rng(1050)
    worst_distance_error = 0.0
    for _ in range(100):
        rotation, _ = np.linalg.qr(rng.normal(size=(3, 3)))
        if np.linalg.det(rotation) < 0:
            rotation[:, 0] *= -1
        x, y = rng.normal(size=(2, 3))
        translation = np.array([-3, 2, 1])
        difference = (rotation @ x + translation) - (rotation @ y + translation)
        error = abs(np.linalg.norm(difference) - np.linalg.norm(x - y))
        worst_distance_error = max(worst_distance_error, error)
    check(worst_distance_error < 1e-12,
          f"Q4: 100 rigid motions preserve distance; max error {worst_distance_error:.3e}")

    # Exact rational DLT is independent of the normalized floating-point solver.
    world_h = sp.Matrix(WORLD.tolist()).applyfunc(sp.Rational)
    world_h = world_h.col_join(sp.ones(1, 6))
    rows = []
    for i in range(6):
        point = list(world_h[:, i])
        u, v = (sp.Integer(IMAGE[j, i]) for j in (0, 1))
        rows.extend([point + [0] * 4 + [-u * x for x in point],
                     [0] * 4 + point + [-v * x for x in point]])
    exact_design = sp.Matrix(rows)
    exact_camera = sp.Matrix([[180, 0, 0, 280], [0, 180, 0, 220], [0, 0, 0, 1]])
    exact_vector = sp.Matrix(list(exact_camera))
    check(exact_design.rank() == 11 and exact_design * exact_vector == sp.zeros(12, 1),
          "Q5: exact rational DLT has rank 11 and the stated null vector")
    camera, projected, errors, _, rank = estimate_camera()
    expected = np.array(exact_camera, dtype=float) / np.sqrt(191601)
    check(rank == 11 and np.allclose(camera, expected, atol=1e-12, rtol=0)
          and abs(np.linalg.norm(camera, "fro") - 1) < 1e-12
          and errors.max() < 1e-9,
          "Q5: computed unit-norm camera agrees with exact solution and all six pixels")

    point_h, projected, errors, _ = triangulate()
    check(np.allclose(point_h, [0, 0, 0.4, 1], atol=1e-12, rtol=0)
          and errors.max() < 1e-9 and (P1 @ point_h)[2] > 0
          and (P2 @ point_h)[2] > 0,
          "Q6: triangulation agrees with disparity depth and reprojects in both views")
    # Also verify the solution directly with exact arithmetic.
    exact_point = sp.Matrix([0, 0, sp.Rational(2, 5), 1])
    for matrix, pixel in ((P1, [400, 250]), (P2, [385, 250])):
        q = sp.Matrix(matrix.astype(int).tolist()) * exact_point
        check([q[0] / q[2], q[1] / q[2]] == pixel,
              f"Q6: exact reprojection gives {pixel}")

    essential = sp.Matrix([[0, 0, 0], [0, 0, -3], [0, 3, 0]])
    check(essential.rank() == 2 and essential.T == -essential,
          "Q7: E is the rank-two skew matrix of translation (3, 0, 0)")
    check(essential * sp.Matrix([280, 200, 1]) == sp.Matrix([0, -3, 600]),
          "Q8: epipolar line is (0, -3, 600), or y = 200")
    # Verify the chosen E convention on independent 3D points.
    for xyz in rng.uniform([1, 1, 1], [5, 5, 10], size=(20, 3)):
        p1 = xyz / xyz[2]
        xyz2 = xyz + np.array([3, 0, 0])
        p2 = xyz2 / xyz2[2]
        if abs(p2 @ np.array(essential, dtype=float) @ p1) >= 1e-12:
            raise AssertionError("Q7/Q8: epipolar constraint failed")
    print("PASS: Q7/Q8: p2.T E p1 = 0 for 20 independently projected 3D points")

    squared_error = sp.Rational(557, 2) ** 2 + sp.Rational(399, 2) ** 2
    check(squared_error == sp.Rational(234725, 2),
          f"Q9: squared error = 117362.5; error = {float(sp.sqrt(squared_error)):.10f} px")
    orthographic = sp.Matrix([[1, 0, 0], [0, 1, 0]])
    check(orthographic * sp.Matrix([5, 4, 8]) == sp.Matrix([5, 4]),
          "Q10: unit-scale orthographic image is (5, 4)")
    print("All checks passed. Numerical checks supplement the written proofs.")


if __name__ == "__main__":
    main()
