function gcd_custom(a, b)
    # Вычисление наибольшего общего делителя
    while b != 0
        a, b = b, a % b
    end
    return a
end
