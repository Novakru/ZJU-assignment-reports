"""Q10: unit-scale orthographic projection along +Z."""
import sympy as sp


def orthographic_projection():
    projection = sp.Matrix([[1, 0, 0], [0, 1, 0]])
    point = sp.Matrix([5, 4, 8])
    return projection * point


if __name__ == "__main__":
    image = orthographic_projection()
    print("Orthographic image point:", tuple(image))
