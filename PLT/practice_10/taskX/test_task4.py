import json
from queue import Queue

from sqlalchemy import create_engine

from task4 import orm_report, populate, sql_report, validate_period


def check_canonical_dates() -> None:
    validate_period("2026-06-01", "2026-06-11")
    cases = (
        ("20260601", "2026-06-11"),
        ("2026-W23-1", "2026-06-11"),
        ("2026-06-01", "20260611"),
        ("2026-06-01", "2026-W24-4"),
    )
    for start, stop in cases:
        for method in (
            lambda: orm_report(None, start, stop, True),
            lambda: sql_report(None, start, stop),
        ):
            try:
                method()
            except ValueError as error:
                assert "canonical YYYY-MM-DD" in str(error)
            else:
                raise AssertionError("noncanonical date accepted")
    print("CANONICAL_DATES: VALID=1 REJECTED=8 OK")


def apply_delivery(message: bytes, reports: dict[str, list]) -> bool:
    envelope = json.loads(message)
    if not isinstance(envelope, dict):
        raise ValueError("invalid envelope")
    request_id = envelope.get("request_id")
    rows = envelope.get("rows")
    if not isinstance(request_id, str) or not request_id:
        raise ValueError("invalid request_id")
    if not isinstance(rows, list) or len(rows) > 5000:
        raise ValueError("invalid rows")
    identities = set()
    for row in rows:
        if not isinstance(row, list) or len(row) != 4:
            raise ValueError("invalid row")
        identity, name, items, total = row
        if type(identity) is not int or identity in identities:
            raise ValueError("invalid or duplicate order")
        identities.add(identity)
        if not isinstance(name, str) or not isinstance(items, list):
            raise ValueError("invalid fields")
        if type(total) is not int:
            raise ValueError("invalid total")
        for item in items:
            if not isinstance(item, list) or len(item) != 3:
                raise ValueError("invalid item")
            title, quantity, price = item
            if not isinstance(title, str):
                raise ValueError("invalid title")
            if type(quantity) is not int or quantity <= 0:
                raise ValueError("invalid quantity")
            if type(price) is not int or price < 0:
                raise ValueError("invalid price")
        if total != sum(item[1] * item[2] for item in items):
            raise ValueError("incorrect total")
    if request_id in reports:
        if reports[request_id] != rows:
            raise ValueError("request_id reused with different data")
        return False
    reports[request_id] = rows
    return True


def check_duplicate_delivery() -> None:
    engine = create_engine("sqlite://")
    try:
        populate(engine)
        rows = orm_report(engine, "2026-06-01", "2026-06-11", True)
        envelope = {"request_id": "report-june-2026", "rows": rows}
        message = json.dumps(envelope).encode("utf-8")
        transport: Queue[bytes] = Queue()
        transport.put(message)
        transport.put(message)
        reports: dict[str, list] = {}
        applied = sum(
            apply_delivery(transport.get_nowait(), reports) for _ in range(2)
        )
        assert transport.empty()
        assert applied == 1 and len(reports) == 1
        assert reports[envelope["request_id"]] == json.loads(message)["rows"]
        assert len(reports[envelope["request_id"]]) == 140
        altered = {"request_id": envelope["request_id"], "rows": []}
        try:
            apply_delivery(json.dumps(altered).encode("utf-8"), reports)
        except ValueError as error:
            assert "different data" in str(error)
        else:
            raise AssertionError("conflicting request_id accepted")
    finally:
        engine.dispose()
    print("APP_DELIVERY: DELIVERIES=2 APPLIED=1 DUPLICATES=1 ROWS=140 OK")
    print("REQUEST_ID_COLLISION: REJECTED=1 OK")


if __name__ == "__main__":
    check_canonical_dates()
    check_duplicate_delivery()
