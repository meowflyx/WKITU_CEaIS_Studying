# Валидация номера карты
def validate_card(number: str)->bool:
    
    return len(''.join(num for num in number if num.isdigit())) == 16

# Проверка по алгоритму Луна
def shorter_luhns_check(number: str)->bool:

    if not validate_card(number):
        return False

    card_number = ''.join(num for num in number if num.isdigit())

    '''Чисто теоретически такой подход не имеет смысла, т.к мы ранее
    проверяем карту на наличие 16 символов, а метод с reversed_digits
    предполагает что длина карты может быть разной.'''
    reversed_digits = card_number[::-1]

    total_sum = sum(int(d) for d in reversed_digits[::2]) + \
                sum(int(d) * 2 - 9 if int(d) * 2 > 9 else int(d) * 2 for d in reversed_digits[1::2])

    return total_sum % 10 == 0

# Вызов функции
card_number = input("Введите номер карты: ")

# Функция возвращает True, если карта валидная, и False, если нет. Выводим результат.
result = shorter_luhns_check(card_number)

if result:
    print("Карта ВАЛИДНАЯ!")
    input("Нажмите Enter для выхода...")
else:
    print("Карта НЕВАЛИДНАЯ!")
    input("Нажмите Enter для выхода...")
    