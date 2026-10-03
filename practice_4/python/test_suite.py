from models import Event, UserStats
from imperative import process_imperative
from oop import process_oop
from functional import process_functional

def run_all_tests() -> None:
    test_cases: dict[str, list[Event]] = {
        "1. Пустой журнал": [],
        "2. Один пользователь": [
            Event(100, "u1", "login", 10),
            Event(200, "u1", "click", 5)
        ],
        "3. Граница 30 минут (1800с)": [
            Event(0, "u1", "view", 5),
            Event(1800, "u1", "view", 5),
            Event(3601, "u1", "view", 5)
        ],
        "4. События с нулевой длительностью": [
            Event(100, "u1", "ping", 0),
            Event(200, "u1", "ping", 0)
        ],
        "5. Неупорядоченный журнал": [
            Event(5000, "u1", "logout", 10),
            Event(100, "u1", "login", 10),
            Event(200, "u1", "click", 10)
        ],
        "6. Множественные сеансы": [
            Event(0, "u1", "a", 10),
            Event(2000, "u1", "b", 10),
            Event(5000, "u1", "a", 10)
        ],
        "7. Несколько пользователей": [
            Event(100, "u1", "click", 10),
            Event(100, "u2", "view", 20)
        ],
        "8. Равные частоты типов": [
            Event(100, "u1", "b_type", 10),
            Event(200, "u1", "a_type", 10)
        ]
    }

    implementations = [process_imperative, process_oop, process_functional]

    for name, events in test_cases.items():
        results = [fn(events) for fn in implementations]
        # Проверяем, что результаты всех трех функций абсолютно идентичны
        assert results[0] == results[1] == results[2], f"Ошибка на тесте '{name}'"

    print("Все 8 тестов успешно пройдены для всех трех реализаций!")

if __name__ == "__main__":
    run_all_tests()