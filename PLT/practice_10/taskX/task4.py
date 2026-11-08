
from __future__ import annotations

import json
import platform
import sqlite3
from collections import defaultdict
from datetime import date, timedelta
from http.client import RemoteDisconnected
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from statistics import median
from tempfile import TemporaryDirectory
from threading import Thread
from time import perf_counter, sleep
from urllib.error import HTTPError
from urllib.request import urlopen

import sqlalchemy
from sqlalchemy import (
    ForeignKey, Integer, String, create_engine, event, select, text,
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, Session, joinedload, mapped_column, relationship,
)


class Base(DeclarativeBase):
    pass


class Customer(Base):

    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)


class Order(Base):

    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    created_at: Mapped[str] = mapped_column(String)
    customer: Mapped[Customer] = relationship()
    items: Mapped[list[Item]] = relationship(order_by="Item.id")


class Item(Base):

    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    title: Mapped[str] = mapped_column(String)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[int] = mapped_column(Integer)


QUERY = """
SELECT o.id, c.name, i.id AS item_id, i.title, i.quantity, i.unit_price,
       SUM(i.quantity * i.unit_price) OVER (PARTITION BY o.id) AS total
FROM orders AS o
JOIN customers AS c ON c.id = o.customer_id
JOIN items AS i ON i.order_id = o.id
WHERE o.created_at >= :start AND o.created_at < :stop
ORDER BY total DESC, o.id, i.id
"""


def validate_period(start: str, stop: str) -> None:
    parsed_start = date.fromisoformat(start)
    parsed_stop = date.fromisoformat(stop)
    if start != parsed_start.isoformat() or stop != parsed_stop.isoformat():
        raise ValueError("dates must use canonical YYYY-MM-DD format")
    if parsed_start >= parsed_stop:
        raise ValueError("start must precede stop")


def orm_report(engine, start: str, stop: str, eager: bool) -> list[tuple]:
    validate_period(start, stop)
    statement = select(Order).where(Order.created_at >=
                                    start, Order.created_at < stop)
    if eager:
        statement = statement.options(joinedload(
            Order.customer), joinedload(Order.items))
    with Session(engine) as session:
        orders = session.scalars(statement).unique().all()
        result = []
        for order in orders:
            items = tuple((item.title, item.quantity, item.unit_price)
                          for item in order.items)
            total = sum(quantity * price for _, quantity, price in items)
            result.append((order.id, order.customer.name, items, total))
    return sorted(result, key=lambda row: (-row[3], row[0]))


def sql_report(engine, start: str, stop: str) -> list[tuple]:
    validate_period(start, stop)
    with engine.connect() as connection:
        rows = connection.execute(
            text(QUERY), {"start": start, "stop": stop}).mappings().all()
    groups = defaultdict(list)
    names = {}
    totals = {}
    for row in rows:
        identity = row["id"]
        groups[identity].append(
            (row["title"], row["quantity"], row["unit_price"]))
        names[identity] = row["name"]
        totals[identity] = row["total"]
    return [(identity, names[identity], tuple(items), totals[identity])
            for identity, items in groups.items()]


def populate(engine) -> None:
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(text("PRAGMA automatic_index=OFF"))
        connection.execute(Customer.__table__.insert(), [
            {"id": index, "name": f"Контрагент {index}"}
            for index in range(1, 5001)
        ])
        connection.execute(Order.__table__.insert(), [
            {"id": index, "customer_id": index,
             "created_at": (
                 date(2026, 1, 1) + timedelta(days=index % 365)
             ).isoformat()}
            for index in range(1, 5001)
        ])
        connection.execute(Item.__table__.insert(), [
            {"id": (index - 1) * 3 + position + 1, "order_id": index,
             "title": f"Товар {position + 1}", "quantity": position + 1,
             "unit_price": 100 + index % 91}
            for index in range(1, 5001) for position in range(3)
        ])


def plan(engine, start: str, stop: str) -> list[str]:
    with engine.connect() as connection:
        return [row[3] for row in connection.execute(
            text("EXPLAIN QUERY PLAN " + QUERY), {"start": start, "stop": stop}
        )]


def check_faults(reference: list[tuple]) -> dict[str, str]:
    class Handler(BaseHTTPRequestHandler):

        def log_message(self, format_string, *arguments):
            return None

        def do_GET(self):
            mode = self.path.removeprefix("/")
            if mode == "disconnect":
                self.connection.close()
                return
            if mode == "error":
                self.send_error(503)
                return
            if mode == "slow":
                sleep(0.06)
            data = reference * 2 if mode == "duplicate" else reference
            payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            try:
                self.wfile.write(payload)
            except (
                BrokenPipeError, ConnectionResetError, ConnectionAbortedError,
            ):
                return

    def read_report(url: str) -> list:
        with urlopen(url, timeout=0.02) as response:
            records = json.loads(response.read(1_000_001))
        if not isinstance(records, list) or len(records) > 5000:
            raise ValueError("invalid report size")
        identities = set()
        for row in records:
            if not isinstance(row, list) or len(row) != 4:
                raise ValueError("invalid record")
            identity, name, items, total = row
            if type(identity) is not int or identity in identities:
                raise ValueError("duplicate or invalid id")
            identities.add(identity)
            if not isinstance(
                    name,
                    str) or type(total) is not int or not isinstance(
                    items,
                    list):
                raise ValueError("invalid field type")
            for item in items:
                if (not isinstance(item, list) or len(item) != 3
                        or not isinstance(item[0], str)
                        or type(item[1]) is not int or item[1] <= 0
                        or type(item[2]) is not int or item[2] < 0):
                    raise ValueError("invalid item")
            if total != sum(item[1] * item[2] for item in items):
                raise ValueError("invalid total")
        return records

    results = {}
    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        server.daemon_threads = True
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_port}"
        assert len(read_report(base + "/normal")) == len(reference)
        for mode, exception_type in (
            ("slow", TimeoutError), ("error", HTTPError),
            ("disconnect", RemoteDisconnected), ("duplicate", ValueError),
        ):
            try:
                read_report(base + "/" + mode)
            except exception_type as error:
                results[mode] = type(error).__name__
            else:
                raise AssertionError(f"fault not detected: {mode}")
        server.shutdown()
        thread.join(timeout=2)
    return results


def main() -> None:
    folder = Path(__file__).parent
    observations = []
    log = []
    start, stop = "2026-06-01", "2026-06-11"
    with TemporaryDirectory(prefix="plt10_") as temporary:
        engine = create_engine(
            f"sqlite:///{Path(temporary) / 'orders.sqlite'}")
        populate(engine)
        statements = []

        def capture(
                connection,
                cursor,
                statement,
                parameters,
                context,
                executemany):
            if statement.lstrip().upper().startswith("SELECT"):
                statements.append((statement, repr(parameters)))

        event.listen(engine, "before_cursor_execute", capture)
        reference = orm_report(engine, start, stop, False)
        assert len(reference) == 140
        methods = {
            "lazy": lambda: orm_report(engine, start, stop, False),
            "eager": lambda: orm_report(engine, start, stop, True),
            "sql": lambda: sql_report(engine, start, stop),
        }
        plans = {}
        for stage in ("before_index", "after_index"):
            if stage == "after_index":
                with engine.begin() as connection:
                    connection.execute(
                        text(
                            "CREATE INDEX ix_orders_date "
                            "ON orders(created_at)"
                        )
                    )
                    connection.execute(
                        text("CREATE INDEX ix_items_order ON items(order_id)")
                    )
                    connection.execute(text("ANALYZE"))
            plans[stage] = plan(engine, start, stop)
            for name, method in methods.items():
                for _ in range(3):
                    assert method() == reference
                times = []
                counts = []
                for trial in range(1, 8):
                    statements.clear()
                    began = perf_counter()
                    result = method()
                    elapsed = perf_counter() - began
                    assert result == reference
                    times.append(elapsed)
                    counts.append(len(statements))
                    if trial == 1:
                        log.append(
                            f"{stage} {name}: {
                                len(statements)} SELECT statements")
                        for number, (statement, parameters) in enumerate(
                                statements, 1):
                            log.append(
                                f"{number}. {
                                    statement.strip()} | {parameters}")
                assert len(set(counts)) == 1
                observations.append({"stage": stage,
                                     "method": name,
                                     "requests": counts[0],
                                     "median_s": median(times),
                                     "min_s": min(times),
                                     "max_s": max(times),
                                     "samples_s": times})
        for method in (lambda a, b: orm_report(engine, a, b, True),
                       lambda a, b: sql_report(engine, a, b)):
            assert method("2030-01-01", "2030-01-02") == []
            assert len(method("0001-01-01", "9999-12-31")) == 5000
            for first, last in (("bad", stop), (stop, start)):
                try:
                    method(first, last)
                except ValueError:
                    pass
                else:
                    raise AssertionError("invalid period accepted")
        engine.dispose()
    faults = check_faults(reference)
    result = {
        "faults": faults,
        "python": platform.python_version(),
        "sqlalchemy": sqlalchemy.__version__,
        "sqlite": sqlite3.sqlite_version,
        "orders": 5000,
        "items": 15000,
        "selected_orders": 140,
        "warmup": 3,
        "trials": 7,
        "observations": observations,
        "plans": plans}
    folder.joinpath("results.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8")
    folder.joinpath("queries.txt").write_text(
        "\n".join(log) + "\n", encoding="utf-8")
    for row in observations:
        print(
            f"{
                row['stage']} {
                row['method']}: SELECTS={
                row['requests']} " f"MEDIAN={
                    row['median_s']:.9f} MIN={
                        row['min_s']:.9f} MAX={
                            row['max_s']:.9f}")
    print("FAULTS=" + json.dumps(faults, sort_keys=True))
    print("ORM_SQL_EQUAL ORDERS=140 TRIALS=7 WARMUP=3 EDGE_CASES=8 OK")


if __name__ == "__main__":
    main()
