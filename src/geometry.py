import numpy as np


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

    def dist_to_point(self, point):
        return np.linalg.norm(point.__values - self.__values)

    def copy(self):
        return Point(self.x, self.y)

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

    def get_a(self): return self.__values[0]

    def set_a(self, a): self.__values[0] = a

    def get_b(self): return self.__values[1]

    def set_b(self, b): self.__values[1] = b

    @property
    def values(self): return self.__values

    a = property(get_a, set_a)
    b = property(get_b, set_b)


if __name__ == '__main__':
    a, b = Point(1, 2), Point(2, 1)
    seg = Segment(a, b)
    print(seg)
