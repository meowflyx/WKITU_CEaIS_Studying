"""Практика 4, задание 3: журнал редактора и цена копирования."""

import sys
import tracemalloc
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Lock
from time import perf_counter

BLOCK_SIZE = 256
LINE = "строка"
EDIT = "вставка"


def insert_copy(lines: list[str], index: int, value: str) -> list[str]:
    changed = lines.copy()
    changed.insert(index, value)
    return changed


def delete_copy(lines: list[str], index: int) -> list[str]:
    changed = lines.copy()
    changed.pop(index)
    return changed


def insert_shared(
    blocks: tuple[tuple[str, ...], ...], index: int, value: str
) -> tuple[tuple[str, ...], ...]:
    offset = index
    for number, block in enumerate(blocks):
        if offset <= len(block):
            changed = block[:offset] + (value,) + block[offset:]
            replacement = (
                (changed,)
                if len(changed) <= BLOCK_SIZE
                else (changed[:128], changed[128:])
            )
            return blocks[:number] + replacement + blocks[number + 1 :]
        offset -= len(block)
    raise IndexError(index)


def delete_shared(
    blocks: tuple[tuple[str, ...], ...], index: int
) -> tuple[tuple[str, ...], ...]:
    offset = index
    for number, block in enumerate(blocks):
        if offset < len(block):
            changed = block[:offset] + block[offset + 1 :]
            replacement = (changed,) if changed or len(blocks) == 1 else ()
            return blocks[:number] + replacement + blocks[number + 1 :]
        offset -= len(block)
    raise IndexError(index)


def make_shared(size: int) -> tuple[tuple[str, ...], ...]:
    if size == 0:
        return ((),)
    return tuple(
        tuple([LINE] * min(BLOCK_SIZE, size - index))
        for index in range(0, size, BLOCK_SIZE)
    )


def run_operations(style: str, size: int, count: int = 100_000) -> int:
    """Чередует вставку и удаление в середине, хранит 100 шагов отката."""
    index = size // 2
    history: deque = deque(maxlen=100)
    if style == "mutable":
        lines = [LINE] * size
        for step in range(count):
            if step % 2 == 0:
                lines.insert(index, EDIT)
                history.append(("delete", index, LINE))
            else:
                removed = lines.pop(index)
                history.append(("insert", index, removed))
        return len(lines)

    if style == "copy":
        state = [LINE] * size
        insert = insert_copy
        delete = delete_copy
    else:
        state = make_shared(size)
        insert = insert_shared
        delete = delete_shared
    for step in range(count):
        history.append(state)
        state = insert(state, index, EDIT) if step % 2 == 0 else delete(state, index)
    return len(state) if style == "copy" else sum(map(len, state))


def measure(style: str, size: int, count: int = 100_000) -> tuple[float, float]:
    tracemalloc.start()
    run_operations(style, size, 100)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    start = perf_counter()
    result_size = run_operations(style, size, count)
    seconds = perf_counter() - start
    assert result_size == size
    return seconds, peak / 1024**2


def undo_mutable(lines: list[str], history: list[tuple[str, int, str]]) -> None:
    for operation, index, value in reversed(history):
        if operation == "delete":
            lines.pop(index)
        else:
            lines.insert(index, value)


def measure_undo(style: str, size: int = 1_000) -> float:
    index = size // 2
    if style == "mutable":
        lines = [LINE] * size
        history = []
        for _ in range(100):
            lines.insert(index, EDIT)
            history.append(("delete", index, LINE))
        start = perf_counter()
        undo_mutable(lines, history)
    else:
        state = [LINE] * size if style == "copy" else make_shared(size)
        insert = insert_copy if style == "copy" else insert_shared
        history = []
        for _ in range(100):
            history.append(state)
            state = insert(state, index, EDIT)
        start = perf_counter()
        state = history[0]
    elapsed = perf_counter() - start
    restored = (
        lines
        if style == "mutable"
        else (
            [value for block in state for value in block]
            if style == "shared"
            else state
        )
    )
    assert restored == [LINE] * size
    return elapsed * 1_000_000


def threaded_run(
    style: str, size: int, reads_per_write: int, writes: int = 200
) -> float:
    """Один поток пишет, три получают снимки; у всех снимок независим от записи."""
    lock = Lock()
    start_together = Barrier(4)
    index = size // 2
    state = [LINE] * size if style == "mutable" else make_shared(size)

    def writer() -> None:
        nonlocal state
        start_together.wait()
        for step in range(writes):
            with lock:
                if style == "mutable":
                    if step % 2 == 0:
                        state.insert(index, EDIT)
                    else:
                        state.pop(index)
                else:
                    state = (
                        insert_shared(state, index, EDIT)
                        if step % 2 == 0
                        else delete_shared(state, index)
                    )

    def reader(count: int) -> None:
        start_together.wait()
        for _ in range(count):
            with lock:
                snapshot = state.copy() if style == "mutable" else state
            first_line = snapshot[0] if style == "mutable" else snapshot[0][0]
            assert first_line == LINE

    counts = [reads_per_write * writes // 3] * 3
    for number in range(reads_per_write * writes % 3):
        counts[number] += 1
    start = perf_counter()
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = [pool.submit(writer)]
        jobs.extend(pool.submit(reader, count) for count in counts)
        for job in jobs:
            job.result()
    return perf_counter() - start


def test_behavior() -> None:
    for size in (0, 1, 1_000):
        index = size // 2
        expected = [LINE] * size
        copied = expected.copy()
        shared = make_shared(size)
        previous_copy = copied
        previous_shared = shared
        expected.insert(index, EDIT)
        copied = insert_copy(copied, index, EDIT)
        shared = insert_shared(shared, index, EDIT)
        assert list(copied) == expected
        assert [value for block in shared for value in block] == expected
        if size == 1_000:
            assert previous_shared[0] is shared[0]
        assert list(previous_copy) == [LINE] * size
        assert [value for block in previous_shared for value in block] == [LINE] * size
        expected.pop(index)
        copied = delete_copy(copied, index)
        shared = delete_shared(shared, index)
        assert list(copied) == expected
        assert [value for block in shared for value in block] == expected
    for style in ("mutable", "copy", "shared"):
        assert run_operations(style, 1_000, 100) == 1_000
        assert run_operations(style, 1_000, 1) == 1_001
        measure_undo(style)
    empty = delete_shared(make_shared(1), 0)
    assert insert_shared(empty, 0, EDIT) == ((EDIT,),)
    for delete in (
        lambda: [LINE].pop(2),
        lambda: delete_copy([LINE], 2),
        lambda: delete_shared(make_shared(1), 2),
    ):
        try:
            delete()
        except IndexError:
            continue
        raise AssertionError("Удаление вне документа не вызвало IndexError")


def main() -> None:
    test_behavior()
    print("Проверка вставки, удаления, отката и 100 операций: OK")
    if "--bench" not in sys.argv:
        return
    for size in (1_000, 1_000_000):
        for style in ("mutable", "copy", "shared"):
            seconds, peak = measure(style, size)
            print(
                f"100000, {size}, {style}: {seconds:.3f} c; peak {peak:.2f} MiB",
                flush=True,
            )
    for style in ("mutable", "copy", "shared"):
        print(f"undo 100, {style}: {measure_undo(style):.1f} мкс")
    for ratio in (0, 1, 2, 5, 10, 100):
        for style in ("mutable", "shared"):
            times = sorted(
                threaded_run(style, 1_000, ratio, writes=10_000) for _ in range(3)
            )
            print(f"threads, reads/write {ratio}, {style}: {times[1]:.4f} c")


if __name__ == "__main__":
    main()
