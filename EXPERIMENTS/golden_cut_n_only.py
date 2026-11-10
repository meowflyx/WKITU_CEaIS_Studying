import time


# Находим число по номеру n; без аргумента берем десятое.
def get_n_of_fi(n: int = 10) -> tuple[str, int, str, float | None]:
    if n < 1:  # Проверяем, что номер начинается с единицы.
        raise ValueError("n должно быть выше нуля")  # Завершаем с ошибкой.

    previous, number = 1, 0  # Стартовые значения для двоичных прыжков.
    for bit in bin(n)[2:]:  # Читаем биты номера слева направо, убрав 0b.
        previous, number = (
            previous * previous + number * number,  # Новый сосед при удвоении.
            number * (2 * previous + number),  # Число для удвоенного номера.
        )
        if bit == "1":  # Для единицы после удвоения нужен еще один шаг.
            previous, number = number, previous + number  # Следующая пара.

    return (
        "n is",  # Подпись найденного числа.
        number,  # Само n-е число Фибоначчи.
        "neighbors relation",  # Подпись отношения соседей.
        None if n == 1 else number / previous,  # Делим на соседа, если n > 1.
    )


def get_n_of_fi_verbose(
    n: int = 10, delay: float = 0.5
) -> tuple[str, int, str, float | None]:
    if delay < 0:
        raise ValueError("Задержка должна быть неотрицательной")

    def show(message: str) -> None:
        """Показать каждую строку отдельно и выдержать паузу после нее."""
        for line in message.splitlines():
            print(line, flush=True)
            if delay:
                time.sleep(delay)

    show(f"Ищем {n}-е число Фибоначчи. Проверяем, что n >= 1.")
    if n < 1:
        show("Ошибка: номер должен начинаться с единицы.")
        raise ValueError("n должно быть выше нуля")

    bits = bin(n)[2:]
    previous, number = 1, 0
    index = 0
    show(
        f"Двоичная запись: {bin(n)}. Убираем 0b, получаем маршрут {bits}.\n"
        f"Нужно обработать {len(bits)} битов, а не пройти {n} чисел.\n"
        "Старт: номер 0, previous = 1, number = 0.\n"
        "Это служебная стартовая пара.",
    )

    for step, bit in enumerate(bits, start=1):
        show(
            f"\nШаг {step}/{len(bits)}. Читаем бит {bit}.\n"
            f"Сейчас: номер {index}, previous = {previous}, "
            f"number = {number}.\n"
            f"Удваиваем номер: {index} -> {index * 2}.\n"
            "Обе формулы используют старые значения:\n"
            f"previous <- {previous} * {previous} + {number} * {number}\n"
            f"number <- {number} * (2 * {previous} + {number})",
        )

        previous, number = (
            previous * previous + number * number,
            number * (2 * previous + number),
        )
        index *= 2
        show(
            f"После удвоения: номер {index}, previous = {previous}, number = {number}.",
        )

        if bit == "1":
            show(
                f"Бит 1: делаем еще один шаг, номер {index} -> {index + 1}.\n"
                f"previous <- {number}; number <- {previous} + {number}.",
            )
            previous, number = number, previous + number
            index += 1
        else:
            show("Бит 0: дополнительный шаг пропускаем.")

        show(
            f"Итог шага: номер {index}, F({index}) = {number}.\n"
            f"Предыдущее число: F({index - 1}) = {previous}.",
        )

    relation = None if n == 1 else number / previous
    if n == 1:
        show("Для первого числа отношение не считаем: F(0) = 0.")
    else:
        show(
            f"Отношение соседей: {number} / {previous} = {relation}.",
        )
    show(f"Готово: F({n}) = {number}. Возвращаем результат.")
    input()
    return ("n is", number, "neighbors relation", relation)


if __name__ == "__main__":  # Запускаем пример только при прямом запуске файла.
    print(get_n_of_fi_verbose(30, 3))
