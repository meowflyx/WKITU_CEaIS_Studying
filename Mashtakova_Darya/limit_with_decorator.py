def limit_attempts(func):
    attempts = 0

    # Декоратор для ограничения количества попыток
    def wrapper():
        nonlocal attempts
        if attempts >= 3:
            print("Превышено количество попыток.")
            return
        attempts += 1
        return func()
    
    return wrapper

# Применяем декоратор к функции входа
@limit_attempts
def login():
    username = input("Введите логин: ")
    if username == "admin":
        print("Доступ разрешен.")
    else:
        print("Неверный логин.")