"""Q3: check proportional normals and a basis of plane directions."""
import sympy as sp


def perpendicular_check():
    X, Y, Z = sp.symbols("X Y Z")
    plane = 12 * X + 8 * Y + 28 * Z - 23
    normal = sp.Matrix([sp.diff(plane, v) for v in (X, Y, Z)])
    vector = sp.Matrix([3, 2, 7])
    scale = normal[0] / vector[0]
    directions = normal.T.nullspace()
    dot_products = [vector.dot(d) for d in directions]
    perpendicular = normal == scale * vector and dot_products == [0, 0]
    return normal, scale, dot_products, perpendicular


if __name__ == "__main__":
    normal, scale, dot_products, perpendicular = perpendicular_check()
    print("Plane normal:", tuple(normal))
    print("Normal / given vector scale:", scale)
    print("Dot products with two independent plane directions:", dot_products)
    print("Given vector is perpendicular to the plane:", perpendicular)
