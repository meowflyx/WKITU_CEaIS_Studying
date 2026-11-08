import json
import sqlite3
from contextlib import closing

SCENARIOS = (
    "empty",
    "quantity",
    "missing_file",
    "timeout_once",
    "timeout_always",
    "catalog_contract",
    "capacity",
    "invariant",
    "partial_save",
    "notify",
)


def partial_save_demo() -> tuple[int, int, int]:
    with closing(sqlite3.connect(":memory:")) as database:
        database.execute("CREATE TABLE items(value INTEGER)")
        database.execute("INSERT INTO items VALUES (1)")
        database.commit()
        try:
            raise sqlite3.OperationalError("injected after first committed INSERT")
        except sqlite3.OperationalError:
            after_failure = database.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        database.executemany("INSERT INTO items VALUES (?)", [(1,), (2,)])
        database.commit()
        after_retry = database.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        database.execute("DELETE FROM items")
        database.commit()
        try:
            with database:
                database.execute("INSERT INTO items VALUES (1)")
                raise sqlite3.OperationalError("injected after first INSERT")
        except sqlite3.OperationalError:
            after_rollback = database.execute("SELECT COUNT(*) FROM items").fetchone()[
                0
            ]
        return after_failure, after_retry, after_rollback


def process(scenario: str) -> dict[str, str | int]:
    """Прочитать, проверить, обогатить, сохранить и уведомить о заявке.

    Ключ scenario выбирает детерминированный отказ зависимости. Таймауты
    повторяются не более трёх раз. Необязательное уведомление допускает
    PARTIAL после фиксации данных. Остальные отказы прекращают операцию.
    """
    attempts = 0
    rows = 0
    status = "STOP"
    message = ""
    try:
        if scenario == "missing_file":
            raise FileNotFoundError("input.csv: file not found")
        if scenario == "empty":
            raise ValueError("file: expected at least one row, got empty")
        quantity = -1 if scenario == "quantity" else 2
        if quantity < 1:
            raise ValueError(f"quantity: expected >= 1, got {quantity}")
        if scenario == "capacity":
            raise OverflowError("rows: limit 100, got 101")
        for attempts in range(1, 4):
            try:
                if scenario == "timeout_always" or (
                    scenario == "timeout_once" and attempts == 1
                ):
                    raise TimeoutError("catalog: deadline exceeded")
                code = "" if scenario == "catalog_contract" else "SKU1"
                if not code:
                    raise ValueError("catalog.code: required nonempty value")
                break
            except TimeoutError:
                if attempts == 3:
                    raise
        total = -1 if scenario == "invariant" else quantity * 100
        if total < 0:
            raise ArithmeticError("internal invariant: total >= 0 violated")
        with closing(sqlite3.connect(":memory:")) as database:
            database.execute("CREATE TABLE items(value INTEGER)")
            with database:
                database.execute("INSERT INTO items VALUES (1)")
                if scenario == "partial_save":
                    raise sqlite3.OperationalError(
                        "injected after first INSERT; rolled back"
                    )
                database.execute("INSERT INTO items VALUES (2)")
            rows = database.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        status = "OK"
        try:
            if scenario == "notify":
                raise ConnectionError("notification unavailable; data saved")
        except ConnectionError as error:
            status = "PARTIAL"
            message = str(error)
    except (
        FileNotFoundError,
        ValueError,
        OverflowError,
        TimeoutError,
        ArithmeticError,
        sqlite3.OperationalError,
    ) as error:
        message = f"{type(error).__name__}: {error}"
    return {
        "scenario": scenario,
        "status": status,
        "attempts": attempts,
        "rows": rows,
        "message": message,
    }


def main() -> None:
    for scenario in SCENARIOS:
        print(json.dumps(process(scenario), ensure_ascii=False))
    print("PARTIAL_SAVE", partial_save_demo())
    assert partial_save_demo() == (1, 3, 0)


if __name__ == "__main__":
    main()
