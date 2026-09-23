# Валидация номера карты
def validate_card(number: str)->bool:

    card_number = ''.join(num for num in number if num.isdigit())
    
    if len(card_number) != 16:
        print("Неверный номер карты!")

    return True

# Проверка по алгоритму Луна
def luhns_check(number: str)->bool:

    if not validate_card(number):
        print("Ошибка: карта не прошла проверку. Убедитесь, что ввели корректный номер.")
        return False

    every_first_number = card_number[::2]
    every_second_number = card_number[1::2]

    processed_digits = []

    for num in every_second_number:

        n = int(num) * 2

        if n > 9:
            
            n = int(n) - 9
        
        processed_digits.append(str(n))

    processed_every_second_number = ''.join(processed_digits)

    numbers_combined = every_first_number + processed_every_second_number

    result = 0

    for number in numbers_combined:

        result += int(number)

    if result % 10 > 0:

        return False
    
    else:
        
        return True

# Вызов функции
card_number = input("Введите номер карты: ")

# Функция возвращает True, если карта валидная, и False, если нет. Выводим результат.
result = luhns_check(card_number)

if result:
    print("Карта ВАЛИДНАЯ!")
    input("Нажмите Enter для выхода...")
else:
    print("Карта НЕВАЛИДНАЯ!")
    input("Нажмите Enter для выхода...")
    