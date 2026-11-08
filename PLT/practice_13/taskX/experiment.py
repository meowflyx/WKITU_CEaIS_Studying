import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

ROOT = Path(__file__).resolve().parent


def run(arguments: list[str], directory: Path) -> dict[str, object]:
    started = perf_counter()
    completed = subprocess.run(
        [sys.executable, "-B", *arguments],
        cwd=directory,
        env=dict(os.environ, PYTHONUTF8="1"),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return {
        "command": "python -B " + " ".join(arguments),
        "exit_code": completed.returncode,
        "seconds": round(perf_counter() - started, 6),
        "output": completed.stdout + completed.stderr,
    }


def main() -> None:
    results = {}
    with TemporaryDirectory(prefix="plt13-experiment-") as temporary:
        directory = Path(temporary)
        for name in (
            "prices.py",
            "prices_before.py",
            "test_prices.py",
            "check.py",
            "pyproject.toml",
            "requirements.txt",
            "integrity.json",
        ):
            shutil.copy2(ROOT / name, directory / name)
        source = (directory / "prices.py").read_bytes()
        (directory / "prices.py").write_bytes(
            (directory / "prices_before.py").read_bytes()
        )
        results["before"] = run(["-m", "unittest", "-v", "test_prices.py"], directory)
        (directory / "prices.py").write_bytes(source)
        results["after"] = run(["check.py"], directory)
        config = directory / "pyproject.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                'select = ["E", "F", "I"]', 'select = ["E"]'
            ),
            encoding="utf-8",
        )
        results["weakened_config"] = run(["check.py"], directory)
        shutil.copy2(ROOT / "pyproject.toml", config)
        test = directory / "test_prices.py"
        test.write_text(
            test.read_text(encoding="utf-8").replace("101, 50), 51", "101, 50), 50"),
            encoding="utf-8",
        )
        results["weakened_test"] = run(["check.py"], directory)
        assert results["before"]["exit_code"] == 1
        assert results["after"]["exit_code"] == 0
        assert results["weakened_config"]["exit_code"] == 1
        assert results["weakened_test"]["exit_code"] == 1
    (ROOT / "results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    for name, result in results.items():
        print(f"{name}: exit={result['exit_code']}, {result['seconds']} s")
    print("EXPERIMENT_OK: 2 defects fixed, config and test weakening detected")


if __name__ == "__main__":
    main()
