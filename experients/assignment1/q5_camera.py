"""Question 5: normalized 3D-to-2D DLT, using the given six columns."""

import numpy as np


WORLD = np.array([
    [0, 1, 0, 1, 0.5, 0.5],
    [0, 0, 1, 1, 0.5, 0],
    [2, 2, 2, 2, 4, 4],
], dtype=float)
IMAGE = np.array([
    [280, 460, 280, 460, 370, 370],
    [220, 220, 400, 400, 310, 220],
], dtype=float)


def normalize_points(points):
    """Center points and set mean distance to sqrt(dimension)."""
    dimension = points.shape[0]
    center = points.mean(axis=1)
    distance = np.linalg.norm(points - center[:, None], axis=0).mean()
    if distance <= np.finfo(float).eps:
        raise ValueError("Coincident points cannot be normalized.")
    scale = np.sqrt(dimension) / distance
    transform = np.eye(dimension + 1)
    transform[:dimension, :dimension] *= scale
    transform[:dimension, -1] = -scale * center
    homogeneous = np.vstack((points, np.ones(points.shape[1])))
    return transform @ homogeneous, transform


def estimate_camera(world=WORLD, image=IMAGE):
    """Solve A p = 0, denormalize, fix sign, and set ||P||_F = 1."""
    if world.shape != (3, 6) or image.shape != (2, 6):
        raise ValueError("This exercise expects six 3D/2D correspondences.")
    world_n, world_transform = normalize_points(world)
    image_n, image_transform = normalize_points(image)
    rows = []
    for point, pixel in zip(world_n.T, image_n.T):
        u, v = pixel[:2] / pixel[2]
        rows.append(np.r_[point, np.zeros(4), -u * point])
        rows.append(np.r_[np.zeros(4), point, -v * point])
    design = np.array(rows)
    _, singular_values, vh = np.linalg.svd(design)
    rank = np.linalg.matrix_rank(design)
    if rank != 11:
        raise ValueError(f"Expected a unique camera up to scale; rank={rank}.")
    camera_n = vh[-1].reshape(3, 4)
    camera = np.linalg.solve(image_transform, camera_n @ world_transform)
    camera /= np.linalg.norm(camera, ord="fro")
    if camera.flat[np.argmax(np.abs(camera))] < 0:
        camera = -camera
    homogeneous = np.vstack((world, np.ones(world.shape[1])))
    projected_h = camera @ homogeneous
    if np.any(np.abs(projected_h[2]) < 1e-12):
        raise ValueError("A supplied point projects to infinity.")
    projected = projected_h[:2] / projected_h[2]
    errors = np.linalg.norm(projected - image, axis=0)
    return camera, projected, errors, singular_values, rank


def main():
    np.set_printoptions(precision=10, suppress=True, linewidth=90)
    camera, projected, errors, _, rank = estimate_camera()
    print("P (Frobenius norm = 1):")
    print(camera)
    print(f"Frobenius norm: {np.linalg.norm(camera, 'fro'):.12f}")
    print(f"Normalized design matrix rank: {rank} / 12")
    print("Reprojected pixels (columns match the assignment):")
    print(projected)
    print(f"Maximum reprojection error (px): {errors.max():.3e}")


if __name__ == "__main__":
    main()
