# валидация номера карты (пишу по приколу потомучто нечего делать)

def validate_card(number: str)->bool:

    card_number = ''.join(num for num in number if num.isdigit())
    
    if len(card_number) != 16:
        print("Неверный номер карты!")

    return True

# проверка луна
    
def luhns_check(number):

    if not validate_card(number):
        print("Ошибка: карта не прошла проверку. Убедитесь, что ввели корректный номер.")

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

        print("Карта НЕ валидная!")

    else:
        
        print("Карта ВАЛИДНАЯ!")

# вызов функции

card_number = input("Введите номер карты: ")

luhns_check(card_number)

    