import time


def timer(func):

    def wrapper(*args, **kwargs):

        start_time = time.time()

        result = func(*args, **kwargs)

        end_time = time.time()
        
        print(f"Функция '{func.__name__}' выполнилась за {end_time - start_time:.4f} секунд")

        return result
    
    return wrapper


@timer
def slow_function(delay):

    print(f"Функция уходит в спячку на {delay} секунд...")

    time.sleep(delay)

    return "Я проснулась!"


result = slow_function(2)
print(result)

