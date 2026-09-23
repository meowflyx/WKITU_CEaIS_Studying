import math


def get_user_point() -> list:
    """
    Запрашивает у пользователя координаты точки с валидацией ввода.

    Returns:
        list: Список из двух целых чисел [x, y].
    """
    while True:
        user_point_input = input("Введите координаты искомой точки в формате X, Y: ")
        try:
            user_point = [int(i.strip()) for i in user_point_input.split(",")]
            if len(user_point) != 2:
                raise ValueError("Нужно ровно два числа")
            return user_point
        except ValueError:
            print("Ошибка! Пожалуйста, введите два целых числа через запятую.")


def is_vertex(user_point: list, triangle: dict) -> str | None:
    """
    Проверяет, совпадает ли точка с одной из вершин треугольника.

    Args:
        user_point (list): Координаты точки [x, y].
        triangle (dict): Словарь с координатами вершин треугольника.

    Returns:
        str | None: Имя вершины (например, "A"), если есть совпадение. Иначе None.
    """
    for name, coords in triangle.items():
        if user_point == coords:
            return name
    return None


def get_dist(p1: list, p2: list) -> float:
    """
    Вычисляет расстояние между двумя точками по теореме Пифагора.

    Args:
        p1 (list): Координаты первой точки [x, y].
        p2 (list): Координаты второй точки [x, y].

    Returns:
        float: Расстояние между точками.
    """
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def is_on_line(user_point: list, triangle: dict) -> str | bool:
    """
    Проверяет, лежит ли точка на одной из сторон треугольника.

    Args:
        user_point (list): Координаты точки [x, y].
        triangle (dict): Словарь с координатами вершин треугольника.

    Returns:
        str | bool: Имя стороны (например, "AB"), если точка на ней. Иначе False.
    """
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


def get_side_indicator(p1: list, p2: list, p: list) -> float:
    """
    Вычисляет индикатор полуплоскости (векторное произведение).
    
    Показывает, с какой стороны от направленного отрезка p1->p2 находится точка p.

    Args:
        p1 (list): Координаты начала отрезка [x, y].
        p2 (list): Координаты конца отрезка [x, y].
        p (list): Координаты проверяемой точки [x, y].

    Returns:
        float: Положительное число (точка слева), отрицательное (справа) или 0 (на линии).
    """
    return (p2[0] - p1[0]) * (p[1] - p1[1]) - (p2[1] - p1[1]) * (p[0] - p1[0])


def is_point_inside(user_point: list, triangle: dict) -> bool:
    """
    Определяет, находится ли точка строго внутри треугольника методом полуплоскостей.

    Args:
        user_point (list): Координаты точки [x, y].
        triangle (dict): Словарь с координатами вершин треугольника.

    Returns:
        bool: True, если точка внутри, иначе False.
    """
    d1 = get_side_indicator(triangle["A"], triangle["B"], user_point)
    d2 = get_side_indicator(triangle["B"], triangle["C"], user_point)
    d3 = get_side_indicator(triangle["C"], triangle["A"], user_point)

    # Точка внутри, если все три индикатора одного знака (исключая 0)
    return (d1 > 0 and d2 > 0 and d3 > 0) or (d1 < 0 and d2 < 0 and d3 < 0)


def main():
    """Основная функция программы, управляющая логикой проверок."""
    triangle = {
        "A": [2, 3],
        "B": [3, 9],
        "C": [5, 7]
    }

    user_point = get_user_point()

    vertex_name = is_vertex(user_point, triangle)
    line_name = is_on_line(user_point, triangle)

    # Проверка 1
    if vertex_name:
        print(f"Точка {user_point} находится на одной из вершин треугольника, "
              f"а именно на вершине {vertex_name}.")
        
    # Проверка 2
    elif line_name:
        print(f"Точка {user_point} находится на одной из линий треугольника, "
              f"а именно на линии {line_name}.")
        
    # Проверка 3: Внутренность
    elif is_point_inside(user_point, triangle):
        print(f"Точка {user_point} находится внутри треугольника.")

    else:
        print(f"Точка {user_point} находится снаружи треугольника.")


if __name__ == "__main__":
    main()