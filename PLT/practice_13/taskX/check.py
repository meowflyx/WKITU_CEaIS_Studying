import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

ROOT = Path(__file__).resolve().parent


def verify_integrity() -> bool:
    expected = json.loads((ROOT / "integrity.json").read_text(encoding="utf-8"))
    for name, digest in expected.items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            print(f"INTEGRITY_FAIL: {name}")
            return False
    print("INTEGRITY_OK")
    return True


def main() -> int:
    started = perf_counter()
    if not verify_integrity():
        return 1
    environment = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
    with TemporaryDirectory(prefix="plt13-build-") as temporary:
        files = ["prices.py", "test_prices.py"]
        stages = [
            ("format", ["-m", "ruff", "format", "--no-cache", *files]),
            ("lint", ["-m", "ruff", "check", "--no-cache", *files]),
            ("types", ["-m", "mypy", "--strict", "--cache-dir", temporary, *files]),
            (
                "build",
                [
                    "-c",
                    "import py_compile,sys; "
                    "py_compile.compile('prices.py', cfile=sys.argv[1], doraise=True)",
                    str(Path(temporary) / "prices.pyc"),
                ],
            ),
            ("tests", ["-B", "-m", "unittest", "-v", "test_prices.py"]),
        ]
        for name, arguments in stages:
            result = subprocess.run(
                [sys.executable, *arguments], cwd=ROOT, env=environment, check=False
            )
            print(f"{name}: exit={result.returncode}", flush=True)
            if result.returncode:
                return result.returncode
    if not verify_integrity():
        return 1
    print(f"CHECK_OK: {perf_counter() - started:.6f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
