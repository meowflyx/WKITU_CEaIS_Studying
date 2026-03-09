import random
import time
import argparse
import miniaudio

def play_simple(filename):
    device = miniaudio.PlaybackDevice()
    stream = miniaudio.stream_file(filename)
    device.start(stream)
    return device, stream


def show_balance(balance: int) -> None:
    print(f"Ваш баланс: {balance}")


def modify_balance(balance: int, amount: int, operation: str = "+") -> int:
        if operation == "+":
            return balance + amount
        elif operation == "-":
            return balance - amount
        elif operation == "*":
            return balance * amount
        else:
            return 0


def interface(balance: int, 
              message: str = "Введите ставку или 'q' для выхода: ") -> str:
    print("="*30)
    show_balance(balance)

    while True:
        user_input = input(message).strip().lower()
        if user_input == "":
            print("Пустой ввод!")
            continue
        if user_input in ["q", "m"]:
            return user_input
        if user_input.isdigit():
            return user_input
        
        print("Введите корректное число или 'q'!")


def casino(balance: int, bet: int) -> int:
    emojis = ["🍏", "🍐", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓", "🫐"]
    if balance < bet:
        print("У тебя нет денег. Иди работай.")
        return balance

    # Анимация
    results = []
    print("Крутим барабаны: ", end="", flush=True)

    for slot in range(3):
        for _ in range(15): #  Количество быстрых смен символа
            char = random.choice(emojis)
            print(f"{char}", end="", flush=True)
            time.sleep(0.05) #  Скорость вращения
            print("\b\b", end="", flush=True) #  Стираем эмодзи

        # Финальный выбор для слота
        final_char = random.choice(emojis)
        results.append(final_char)

        # Не спрашивайте
        if "🍌" == final_char:
            play_simple(r"sounds\banani.mp3")
        elif "🫐" == final_char:
            play_simple(r"sounds\slivi.mp3")
        elif "🍇" == final_char:
            play_simple(r"sounds\vinograd.mp3")
        elif "🍏" == final_char:
            play_simple(r"sounds\yabloki_na_zelenih_est.mp3")

        print(f"{final_char}  ", end="", flush=True) # Фиксируем и ставим пробел
        time.sleep(0.5) # Пауза перед следующим слотом

    print("\n" + "="*30)

    res1, res2, res3 = results
    if res1 == res2 == res3:
        win = bet * 10
        print(f"ДЖЕКПОТ! +{win}")
        return balance + win
    elif res1 == res2 or res2 == res3 or res1 == res3:
        win = bet * 2
        print(f"Два одинаковых. +{win}")
        return balance + win
    
    print(f"Проигрыш. -{bet}")
    return balance - bet


def main(starting_balance: int = 1000):
    balance = starting_balance

    while True:
        action = interface(balance)

        if action == "q":
            print("Пока!")
            break
        
        elif action == "m":
            new_val = input("Введите новый баланс: ")
            if new_val.isdigit():
                balance = int(new_val)
            else:
                print("Ошибка, баланс не изменен.")
        
        else:
            # Здесь action это сумма ставки (строка с числом)
            balance = casino(balance, int(action))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Консольное казино")
    parser.add_argument("--bal", type=int, default=1000, help="Стартовый баланс игрока")
    args = parser.parse_args()
    main(starting_balance=args.bal)