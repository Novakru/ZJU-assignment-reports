"""Question 6: homogeneous linear triangulation with the supplied matrices."""

import numpy as np


P1 = np.array([
    [900, 0, 400, 0],
    [0, 900, 250, 0],
    [0, 0, 1, 0],
], dtype=float)
P2 = np.array([
    [900, 0, 400, -6],
    [0, 900, 250, 0],
    [0, 0, 1, 0],
], dtype=float)
PIXEL1 = np.array([400, 250], dtype=float)
PIXEL2 = np.array([385, 250], dtype=float)


def triangulate(p1=P1, p2=P2, pixel1=PIXEL1, pixel2=PIXEL2):
    """Stack x P_3 - P_1 and y P_3 - P_2 for each view."""
    design = np.vstack([
        pixel1[0] * p1[2] - p1[0],
        pixel1[1] * p1[2] - p1[1],
        pixel2[0] * p2[2] - p2[0],
        pixel2[1] * p2[2] - p2[1],
    ])
    _, singular_values, vh = np.linalg.svd(design)
    if np.linalg.matrix_rank(design) != 3:
        raise ValueError("The correspondence does not determine a unique point.")
    point_h = vh[-1]
    if abs(point_h[3]) < 1e-12:
        raise ValueError("The triangulated point is at infinity.")
    point_h = point_h / point_h[3]
    projected_h = np.vstack((p1 @ point_h, p2 @ point_h))
    if np.any(np.abs(projected_h[:, 2]) < 1e-12):
        raise ValueError("Projection has a zero denominator.")
    projected = projected_h[:, :2] / projected_h[:, 2, None]
    errors = np.linalg.norm(projected - np.vstack((pixel1, pixel2)), axis=1)
    return point_h, projected, errors, singular_values


def main():
    np.set_printoptions(precision=10, suppress=True, linewidth=90)
    point_h, projected, errors, singular_values = triangulate()
    print("Q6: homogeneous linear triangulation")
    print("3D point [X, Y, Z]:")
    print(point_h[:3])
    print("Homogeneous point [X, Y, Z, 1]:")
    print(point_h)
    print("Design singular values:")
    print(singular_values)
    print("Reprojected pixels (rows: view 1, view 2):")
    print(projected)
    print(f"Maximum reprojection error (px): {errors.max():.3e}")
    print(f"Depth in both cameras: {point_h[2]:.10f}")
    print(f"Independent disparity depth 6 / (400 - 385): {6 / 15:.10f}")


if __name__ == "__main__":
    main()
