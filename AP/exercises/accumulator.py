def accumulator(limit=10000000):
    total = 0
    while total < limit:
        value = yield total
        if value is not None:
            total += value
    return "Лимит достигнут"

acc = accumulator()

print(next(acc))
print(acc.send(10))
print(acc.send(5))
print(acc.send(10000000)) #  StopIteration: Лимит достигнут