import math

# Треугольник hard-coded, потому-что мне лень
triangle = {
    "A": [2, 3],
    "B": [3, 9],
    "C": [5, 7]
}


# Цикл для валидации и получения точки от пользователя
invalid_user_point = True
while invalid_user_point:

    user_point_input = input("Введите координаты искомой точки в формате X, Y: ")
    
    try:

        user_point = [int(i.strip()) for i in user_point_input.split(",")]
        
        if len(user_point) != 2:

            raise ValueError("Нужно ровно два числа")
            
        invalid_user_point = False

    except ValueError:

        print("Ошибка! Пожалуйста, введите два целых числа через запятую.")


def is_vertex(user_point, triangle):
    """Совпадает ли user_point с одной из точек в triangle?"""
    for name, coords in triangle.items():
            if user_point == coords:
                return name
    return None


def get_dist(p1, p2):
    """Считает расстояние между двумя точками (Пифагор)"""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def is_on_line(user_point, triangle):
    """Лежит ли user_point на одной из линий треугольника?"""
    # Описываем стороны как пары имен и координат
    sides = [
        ("AB", triangle["A"], triangle["B"]),
        ("BC", triangle["B"], triangle["C"]),
        ("CA", triangle["C"], triangle["A"])
    ]
    
    for name, p1, p2 in sides:
        side_length = get_dist(p1, p2)
        dist_to_p1 = get_dist(user_point, p1)
        dist_to_p2 = get_dist(user_point, p2)
        
        # Если сумма расстояний до концов отрезка равна длине отрезка
        if math.isclose(dist_to_p1 + dist_to_p2, side_length):
            return name
            
    return False


def get_side_indicator(p1: list, p2: list, p: list)->bool:
    """Помогает понять с какой стороны от вектора находится точка p.
    Формула понятным языком: D=(x2​−x1​)(yp​−y1​)−(y2​−y1​)(xp​−x1​)"""
    indicator = (p2[0] - p1[0]) * (p[1] - p1[1]) - (p2[1] - p1[1]) * (p[0] - p1[0])
    return indicator


def is_point_inside(user_point, triangle):
    """Точка внутри или снаружи треугольника?"""
    d1 = get_side_indicator(triangle["A"], triangle["B"], user_point)
    d2 = get_side_indicator(triangle["B"], triangle["C"], user_point)
    d3 = get_side_indicator(triangle["C"], triangle["A"], user_point)

    if (d1 > 0 and d2 > 0 and d3 > 0) or (d1 < 0 and d2 < 0 and d3 < 0):
        return True
    else:
        return False


def main():
    # Первая проверка
    if is_vertex(user_point, triangle):
        print(f"Точка {user_point} находится на одной из вершин треугольника, а именно на "
              f"вершине {is_vertex(user_point, triangle)}")
        
    # Вторая проверка
    elif is_on_line(user_point, triangle):
        print(f"Точка {user_point} находится на одной из линий треугольника, а именно на "
              f"линии {is_on_line(user_point, triangle)}")
        
    # Последняя проверка
    elif is_point_inside(user_point, triangle):
        print(f"Точка {user_point} находится внутри треугольника.")

    else:
        print(f"Точка {user_point} находится снаружи треугольника")

main()