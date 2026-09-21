import dis

numbers = [3, 6, 9]

def greatest_common_divisor(numbers: list[int]) -> int:
    if not numbers:
        raise ValueError("numbers must not be empty")

    divisor = abs(numbers[0])
    for number in numbers[1:]:
        number = abs(number)
        while number:
            divisor, number = number, divisor % number

    return divisor

dis.dis(greatest_common_divisor)