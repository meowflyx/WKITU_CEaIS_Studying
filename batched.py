from collections.abc import Iterable, Iterator
from typing import Any
import itertools

def batched(input_data: Iterable[Any], n: int) -> Iterator[tuple[Any, ...]]:
    """Реализация batched через ручное управление итератором.
    Первая попытка."""
    if n < 1:
        raise ValueError("n must be at least 1")
    
    it = iter(input_data)
    
    while True:
        batch = []
        try:
            for _ in range(n):
                batch.append(next(it))
            
            yield tuple(batch)
            
        except StopIteration:
            if batch:
                yield tuple(batch)
            break

print("Решение 1 методом:")
for chunk in batched("ANDREY", 3):
    print(chunk)


def batched_slice(input_data, n):
    """Второе решение, просто через срезы.
    (горжусь тем, что питонически его написал!)"""
    if n < 1: raise ValueError
    for i in range(0, len(input_data), n):
        yield tuple(input_data[i:i + n])

print("Решение 2 методом:")
for chunk in batched_slice("ANDREY", 3):
    print(chunk)


def batched_zip(input_data, n):
    """Третье решение, через zip. Минус в том, что Если данных не 
    хватает на целый батч (например, осталось 2 элемента, а n=3), zip просто выкинет остаток."""
    if n < 1: raise ValueError
    it = [iter(input_data)] * n
    return zip(*it)

print("Решение 3 методом:")
for chunk in batched_zip("ANDREY", 3):
    print(chunk)