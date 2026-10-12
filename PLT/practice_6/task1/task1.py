"""Четыре наблюдения о присваивании и копировании объектов Python."""

from copy import deepcopy


def default_argument() -> None:
    """Показать повторное использование списка по умолчанию."""
    # намеренно оставлен изменяемый аргумент для опыта
    def add_tag(tags: list[str] = [], tag: str = "новый") -> list[str]:
        tags.append(tag)
        return tags

    print("P1")
    first = add_tag()
    print(first)
    second = add_tag()
    print(second)
    print("same:", first is second)
    assert first is second and second == ["новый", "новый"]


def mutation_and_rebinding() -> None:
    """Отделить изменение общего списка от присваивания локальному имени."""
    def change(items: list[int]) -> None:
        items.append(2)
        items = [99]
        print("local:", items)

    print("P2")
    items = [1]
    alias = items
    change(items)
    print("caller:", items)
    print("same:", items is alias)
    assert items == [1, 2] and items is alias


def shallow_copy() -> None:
    """Проверить общую вложенность при раздельных внешних списках."""
    print("P3")
    source = [[1]]
    copied = source.copy()
    copied[0].append(2)
    copied.append([3])
    print("source:", source)
    print("copy:", copied)
    print("same outer:", source is copied)
    print("same inner:", source[0] is copied[0])
    assert source == [[1, 2]] and copied == [[1, 2], [3]]
    assert source is not copied and source[0] is copied[0]


def deep_copy() -> None:
    """Проверить отделение копии и сохранение повторной внутренней ссылки."""
    print("P4")
    shared = [1]
    source = [shared, shared]
    copied = deepcopy(source)
    copied[0].append(9)
    print("source:", source)
    print("deep:", copied)
    print("same as source:", source[0] is copied[0])
    print("same inside deep:", copied[0] is copied[1])
    assert source == [[1], [1]] and copied == [[1, 9], [1, 9]]
    assert source[0] is not copied[0] and copied[0] is copied[1]


def edge_cases() -> None:
    """Проверить пустой список, большое число, цикл и неверный индекс."""
    empty: list[int] = []
    assert empty.copy() == [] and empty.copy() is not empty
    large = 10**100
    assert deepcopy([large]) == [large]
    cycle = []
    cycle.append(cycle)
    copied = deepcopy(cycle)
    assert copied is not cycle and copied[0] is copied
    try:
        empty[0]
    except IndexError:
        print("Python edge cases: 4/4 OK")
    else:
        raise AssertionError("Ожидался IndexError")


if __name__ == "__main__":
    default_argument()
    mutation_and_rebinding()
    shallow_copy()
    deep_copy()
    print("Python: 4/4 OK")
    edge_cases()
