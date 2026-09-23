import time

def timeout(func, seconds: int = 10):
    '''
    Попытка реализовать декоратор для таймаута функции.
    :param func: функция
    :param seconds: кол-во секунд после которого прерывается выполнение (=10)
    :return: None
    '''

    def wrapper(*args, **kwargs):

        start_time = time.time()

        while True:
            
            elapsed_time = time.time() - start_time

            func(*args, **kwargs)

            '''
            Разве это вообще выполнимая задача?
            БЕЗ асинхронности и мультипоточности?
            Сейчас он просто дождеться пока функция выполнится
            и только потом проверит, превышает ли ее длительность
            нужную нам.
            '''

            if round(elapsed_time) > seconds:

                print(f"Функция выполнялась больше {seconds} секунд! \
                    Прерываю выполнение.")
                
                break

            else:

                pass

    return wrapper


@timeout
def sleepy_function(seconds: int) -> None:
    '''
    Функция которая спит определенное кол-во секунд и логгирует это.
    :param seconds: количество секунд для сна
    :return: None
    '''
    slept_seconds = 0

    while slept_seconds < seconds:
        print(f"Сплю уже {slept_seconds+1} секунд(-ы)...")
        time.sleep(1)
        slept_seconds += 1

    print(f"Выспалась. Спала {slept_seconds} секунд(-ы, -у).")
    return


sleepy_function(10)

