import numpy as np
from math import fabs

EPS = 10 ** -8


class ICopy:

    def copy(self):
        raise NotImplemented


class Point(ICopy):

    def __init__(self, x, y):
        self.__values = np.array([x, y], dtype=np.float32)

    def __str__(self):
        return f"{self.x, self.y}"

    def __repr__(self):
        return f"{self.x, self.y}"

    def __sub__(self, other):
        return Point(*(self.__values - other.__values))

    def __add__(self, other):
        return Point(*(self.__values + other.__values))

    def __mul__(self, other):
        return Point(*(self.__values * other))

    def __del__(self):
        del self.__values

    def distance_to(self, point):
        return np.linalg.norm(point.__values - self.__values)

    def copy(self):
        return Point(self.x, self.y)

    def to_tuple(self):
        return self.x, self.y

    def get_x(self): return self.__values[0]

    def set_x(self, x): self.__values[0] = x

    def get_y(self): return self.__values[1]

    def set_y(self, y): self.__values[1] = y

    @property
    def values(self): return self.__values

    x = property(get_x, set_x)
    y = property(get_y, set_y)


class Segment(ICopy):

    def __init__(self, a: Point, b: Point):
        self.__values = [a, b]

    def __str__(self):
        return f"{self.__values}"

    def __repr__(self):
        return f"{self.__values}"

    def copy(self):
        return Segment(self.a.copy(), self.b.copy())

    def get_line(self):
        x_1, y_1 = self.a.to_tuple()
        x_2, y_2 = self.b.to_tuple()
        A = y_2 - y_1
        B = x_1 - x_2
        C = - x_1 * A - y_1 * B
        return Line(A, B, C)

    def get_a(self): return self.__values[0]

    def set_a(self, a): self.__values[0] = a

    def get_b(self): return self.__values[1]

    def set_b(self, b): self.__values[1] = b

    @property
    def values(self): return self.__values

    a = property(get_a, set_a)
    b = property(get_b, set_b)


class Line(ICopy):

    def __init__(self, A, B, C):
        self.__values = np.array([A, B, C])

    def check_point(self, point):
        x, y = point.x, point.y
        A, B, C = self.A, self.B, self.C
        return A * x + B * y + C

    def reverse_coefs(self):
        self.A, self.B, self.C = -self.A, -self.B, -self.C

    def intersect_with_line(self, line):
        A1, B1, C1 = self.A, self.B, self.C
        A2, B2, C2 = line.A, line.B, line.C
        if fabs(A1 * B2 - A2 * B1) <= EPS:
            return None
        intersect = Point(0, 0)
        intersect.x = -(C1 * B2 - C2 * B1) / (A1 * B2 - A2 * B1)
        intersect.y = -(A1 * C2 - A2 * C1) / (A1 * B2 - A2 * B1)
        return intersect

    def intersect_with_segment(self, segment):
        segment_line = segment.get_line()
        intersect = self.intersect_with_line(segment_line)
        if intersect is None:
            return None
        vec1 = Point(intersect.x - segment.a.x, intersect.y - segment.a.y)
        vec2 = Point(intersect.x - segment.b.x, intersect.y - segment.b.y)
        if vec1.x * vec2.x <= EPS and vec1.y * vec2.y <= EPS:
            return intersect
        return None

    def get_A(self):
        return self.__values[0]

    def set_A(self, A):
        self.__values[0] = A

    def get_B(self):
        return self.__values[1]

    def set_B(self, B):
        self.__values[1] = B

    def get_C(self):
        return self.__values[2]

    def set_C(self, C):
        self.__values[2] = C

    @property
    def values(self):
        return self.__values

    A = property(get_A, set_A)
    B = property(get_B, set_B)
    C = property(get_C, set_C)


class Polygon:

    def __init__(self, segments: list):
        self.segments = segments

    def contains_point(self, point):
        ray = Ray(Segment(point, Point(point.x + 1, point.y)))
        intersects_num = 0
        for segment in self.segments:
            if ray.intersect_with_segment(segment) is not None:
                intersects_num += 1
        return bool(intersects_num % 2)


class Ray:

    def __init__(self, segment: Segment):
        self.main_line = segment.get_line()
        vec = Point(segment.b.y - segment.a.y + segment.a.x,
                    -segment.b.x + segment.a.x + segment.a.y)
        self.side_line = Segment(segment.a, vec).get_line()
        self.point = segment.a
        if self.side_line.check_point(segment.b) < 0:
            self.side_line.reverse_coefs()

    def intersect_with_segment(self, segment: Segment):
        intersect = self.main_line.intersect_with_segment(segment)
        if intersect is not None and self.side_line.check_point(intersect) > 0:
            return intersect
        return None

    def intersect_with_polygon(self, polygon):
        points = []
        for segment in polygon.segments:
            point = self.intersect_with_segment(segment)
            if point is not None:
                points.append(point)

        if len(points) == 0:
            return None
        return min(zip(points,
                       map(lambda p: p.distance_to(self.point), points)),
                   key=lambda pd: pd[1])[0]


if __name__ == '__main__':
    a, b = Point(1, 2), Point(2, 1)
    seg = Segment(a, b)
    print(seg)
