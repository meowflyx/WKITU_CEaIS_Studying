"""Идея: Функция, принимает n. N это член числового ряда Фибоначчи который мы должны вернуть.
Надо будет складывать прошлое и нынешнее число, а так же делить нынешнее на предыдущее что-бы найти отношение.
Думаю сделатьф функцию в функции что-бы был генератор удобный
По итогу мы возвращаем tuple вида ("n is", ЧИСЛО, "neighbors relation", ЧИСЛО (отношение соседних чисел))
Наверное, стоит использовать ленивые вычисления."""


def get_n_of_fi(n: int = 10) -> tuple:
    if n < 1:
        raise ValueError("n должно быть выше нуля")

    def fibonacci():
        previous, current = 1, 1
        yield previous, None  # перед первым ничего нет

        while True:
            yield current, current / previous  # нынешнее число и отношение
            previous, current = current, previous + current

    sequence = fibonacci()

    for _ in range(n):
        number, relation = next(sequence)

    return ("n is", number, "neighbors relation", relation)  # возвращаем tuple


print(get_n_of_fi(30))
