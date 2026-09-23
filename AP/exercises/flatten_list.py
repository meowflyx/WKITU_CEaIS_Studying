my_list = [1, [2, [3, [4, [5, 6], 7], 8], 9], [10, 11], [[12, 13], 14], 15]

def flatten_list_one(input_list: list)->list:
    """Первое решение что пришло в голову. Через рекурсию."""
    flat_list = []
    for item in input_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list_one(item)) #  Оказывется есть метод специально для этой цели.
        else:
            flat_list.append(item)
    return flat_list

def flatten_list_two(input_list: list) -> list:
    """Второе решение что пришло в голову.
    Итеративное, с использованием стека (без рекурсии)."""
    flat_list = []
    stack = [input_list]
    while stack:
        current_item = stack.pop()
        if isinstance(current_item, list):
            # Реверсивный порядок
            stack.extend(reversed(current_item))
        else:
            flat_list.append(current_item)
    return flat_list

def flatten_list_three(input_list: list):
    """Решение через генератор (yield from). 
    Раз уж говорим об итераторах. Возвращает итератор."""
    for item in input_list:
        if isinstance(item, list):
            yield from flatten_list_three(item)
        else:
            yield item

print(f"Тест #1: {flatten_list_one(my_list)}")
print(f"Тест #2: {flatten_list_two(my_list)}")

gen = flatten_list_three(my_list)
print(f"Тест #3 (элемент 1): {next(gen)}")
print(f"Тест #3 (элемент 2): {next(gen)}")
print(f"Тест #3 (элемент 3): {next(gen)}")
print(f"Тест #3 (весь список): {list(flatten_list_three(my_list))}")