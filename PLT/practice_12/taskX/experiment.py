import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

ROOT = Path(__file__).resolve().parent


def run(command: list[str], directory: Path) -> dict[str, str | int | float]:
    started = perf_counter()
    completed = subprocess.run(
        command,
        cwd=directory,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return {
        "command": " ".join(command),
        "exit_code": completed.returncode,
        "seconds": round(perf_counter() - started, 6),
        "output": completed.stdout + completed.stderr,
    }


def main() -> None:
    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    cosmic = shutil.which("cosmic-ray") or str(
        Path(sys.executable).with_name("cosmic-ray.exe")
    )
    report_tool = shutil.which("cr-report") or str(
        Path(sys.executable).with_name("cr-report.exe")
    )
    results: dict[str, object] = {}
    with TemporaryDirectory(prefix="plt12-") as temporary:
        directory = Path(temporary)
        for name in ("test_weak.py", "test_discount.py"):
            shutil.copy2(ROOT / name, directory / name)
        shutil.copy2(ROOT / "discount_buggy.py", directory / "discount.py")
        results["buggy_coverage_run"] = run(
            [
                sys.executable,
                "-m",
                "coverage",
                "run",
                "--branch",
                "--source=discount",
                "-m",
                "unittest",
                "test_weak.py",
            ],
            directory,
        )
        results["buggy_coverage"] = run(
            [sys.executable, "-m", "coverage", "report", "-m"], directory
        )
        results["buggy_strong_tests"] = run(
            [sys.executable, "-m", "unittest", "-v", "test_discount.py"], directory
        )
        for phase, module, tests in (
            ("before", "discount_buggy.py", "test_weak.py"),
            ("fixed_weak", "discount.py", "test_weak.py"),
            ("after", "discount.py", "test_discount.py"),
        ):
            shutil.copy2(ROOT / module, directory / "discount.py")
            config = directory / f"{phase}.toml"
            test_command = f'"{sys.executable}" -B -m unittest {tests}'
            config.write_text(
                "[cosmic-ray]\nmodule-path = 'discount.py'\ntimeout = 5.0\n"
                f"excluded-modules = []\ntest-command = '{test_command}'\n"
                "[cosmic-ray.distributor]\nname = 'local'\n",
                encoding="utf-8",
            )
            results[f"{phase}_baseline"] = run(
                [cosmic, "baseline", config.name], directory
            )
            results[f"{phase}_init"] = run(
                [cosmic, "init", config.name, f"{phase}.sqlite"], directory
            )
            results[f"{phase}_exec"] = run(
                [cosmic, "exec", config.name, f"{phase}.sqlite"], directory
            )
            results[f"{phase}_report"] = run(
                [report_tool, f"{phase}.sqlite", "--show-diff"], directory
            )
            if any(
                results[f"{phase}_{step}"]["exit_code"] != 0
                for step in ("baseline", "init", "exec", "report")
            ):
                print(json.dumps(results, ensure_ascii=False, indent=2))
                raise RuntimeError(f"mutation analysis failed: {phase}")
        results["final_tests"] = run(
            [sys.executable, "-m", "unittest", "-v", "test_discount.py"], directory
        )
    (ROOT / "results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    for key in ("buggy_coverage", "before_report", "after_report", "final_tests"):
        print(key)
        output = results[key]["output"]
        print(
            output
            if key in ("buggy_coverage", "final_tests")
            else "\n".join(output.splitlines()[-4:])
        )
    print("EXPERIMENT_OK")


if __name__ == "__main__":
    main()
