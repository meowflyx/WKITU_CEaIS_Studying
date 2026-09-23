def fibonacci_generator():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

fib = fibonacci_generator()

print(next(fib))
print(next(fib))
print(next(fib))
print(next(fib))
print(next(fib))
print(next(fib))
print(next(fib))

del fib

fib = fibonacci_generator()

for i, val in enumerate(fib):
    if i >= 1000: 
        break
    print(val)