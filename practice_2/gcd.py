def gcd(a, b):
    # Вычисление наибольшего общего делителя
    while b != 0:
        a, b = b, a % b
    return a
