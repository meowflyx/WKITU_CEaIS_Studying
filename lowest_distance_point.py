import math


class Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def round(self, round_level: int):
        self.x = round(self.x, round_level)
        self.y = round(self.y, round_level)


def get_distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)


def find_minimal_distance_point(points):
    current_x = sum(p.x for p in points) / len(points)
    current_y = sum(p.y for p in points) / len(points)
    current_point = Point(current_x, current_y)

    for _ in range(200):
        sum_x = 0.0
        sum_y = 0.0
        sum_weight = 0.0

        for p in points:
            dist = get_distance(current_point, p)
            if dist < 1e-9:
                dist = 1e-9
            
            weight = 1.0 / dist
            sum_x += p.x * weight
            sum_y += p.y * weight
            sum_weight += weight

        current_point.x = sum_x / sum_weight
        current_point.y = sum_y / sum_weight

    current_point.round(3)
    return current_point


if __name__ == "__main__":
    polygon = [
        Point(0.0, 0.0),
        Point(10.0, 0.0),
        Point(5.0, 10.0),
        Point(2.0, 5.0)
    ]
    
    best_point = find_minimal_distance_point(polygon)
    print(f"X: {best_point.x}, Y: {best_point.y}")