def rate_limiter(max_retries: int = 3):
    '''
    Ограничитель кол-ва выполнений функции
    :param max_reties: количество максимальных попыток выполнения функции.
    :return: None
    '''

    def decorator(func):

        user_retries = 1

        def wrapper(*args, **kwargs):

            nonlocal user_retries

            if user_retries > max_retries:

                print(f"Функция не выполнена! Превышено максимальное количество попыток ({max_retries}).")
            
            else:

                user_retries += 1
                return func(*args, **kwargs)

        return wrapper
        
    return decorator


@rate_limiter(max_retries=3)
def my_stupid_ahh_function():
    print("Привет! Я самая бесполезная функция в мире.")

my_stupid_ahh_function()  # Привет! Я самая бесполезная функция в мире.
my_stupid_ahh_function()  # Привет! Я самая бесполезная функция в мире.
my_stupid_ahh_function()  # Привет! Я самая бесполезная функция в мире.
my_stupid_ahh_function()  # Функция не выполнена! Превышено максимальное количество попыток (3).
my_stupid_ahh_function()  # Функция не выполнена! Превышено максимальное количество попыток (3).
my_stupid_ahh_function()  # Функция не выполнена! Превышено максимальное количество попыток (3).