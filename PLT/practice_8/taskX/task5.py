
import csv
import platform
from pathlib import Path
from statistics import median
from timeit import repeat

Request = tuple[int, int]


def calculate(request: Request) -> int:
    identity, cost = request
    if cost < 0:
        raise ValueError("cost must be nonnegative")
    state = identity % 1_000_003
    for _ in range(cost):
        state = (state * 33 + 17) % 1_000_003
    return state


def direct(requests: list[Request]) -> list[int]:
    return [calculate(request) for request in requests]


def cached(requests: list[Request]) -> list[int]:
    cache: dict[Request, int] = {}
    results = []
    for request in requests:
        if request not in cache:
            cache[request] = calculate(request)
        results.append(cache[request])
    return results


def cache_allowed(requests: list[Request]) -> bool:
    return bool(requests) and len(set(requests)) * 4 <= len(requests) and all(
        cost >= 100 for _, cost in requests
    )


def guarded(requests: list[Request]) -> list[int]:
    return cached(requests) if cache_allowed(requests) else direct(requests)


def main() -> None:
    datasets = {
        "repeated_costly": [(0, 1000)] * 1000,
        "unique_costly": [(index, 1000) for index in range(1000)],
        "unique_cheap": [(index, 0) for index in range(1000)],
    }
    for requests in ([], [(0, 0)], [(2, 100), (2, 100)], [(10**30, 1)]):
        assert direct(requests) == cached(requests) == guarded(requests)
    try:
        calculate((0, -1))
    except ValueError:
        pass
    else:
        raise AssertionError("negative cost accepted")
    output = Path(__file__).with_name("results_python.csv")
    with output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("dataset", "method", "trial", "seconds"))
        for name, requests in datasets.items():
            reference = direct(requests)
            for method in (direct, cached, guarded, cache_allowed):
                for _ in range(3):
                    result = method(requests)
                    assert isinstance(result, bool) or result == reference
                times = repeat(lambda: method(requests), repeat=7, number=1)
                assert isinstance(method(requests), bool) or method(
                    requests) == reference
                for trial, elapsed in enumerate(times, 1):
                    writer.writerow(
                        (name, method.__name__, trial, f"{elapsed:.9f}"))
                print(f"{name} {method.__name__}: median={median(times):.9f} "
                      f"min={min(times):.9f} max={max(times):.9f}")
    print(f"PYTHON={platform.python_version()} TRIALS=7 WARMUP=3 "
          "DATASETS=3 EDGE_CASES=5 OK")


if __name__ == "__main__":
    main()
