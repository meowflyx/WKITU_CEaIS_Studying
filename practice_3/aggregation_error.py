# Данные о доходах сотрудников. None = сотрудник отказался ответа (данные скрыты)
salaries: list[Optional[float]] = [1000.0, None, 2000.0]

# Некорректная агрегация: фильтрация None как 0.0
total = sum(s if s is not None else 0.0 for s in salaries)
count = len(salaries)
avg = total / count # Получили 1000.0 (искаженное среднее, хотя должно быть 1500.0 по ответившим)