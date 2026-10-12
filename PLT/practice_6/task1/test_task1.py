"""Сверить повторный запуск программ с сохраненным фактическим выводом."""

from hashlib import sha256
from pathlib import Path
import subprocess
import sys


def main() -> None:
    """Проверить вывод обоих файлов и неизменность предсказаний."""
    folder = Path(__file__).resolve().parent
    protocol = (folder / "execution.txt").read_text(encoding="utf-8")
    prediction_hash = (
        protocol.split("predictions.md SHA-256: ", 1)[1].splitlines()[0]
    )
    assert (
        sha256((folder / "predictions.md").read_bytes()).hexdigest()
        == prediction_hash
    )
    commands = [
        [sys.executable, "-X", "utf8", str(folder / "task1.py")],
        ["julia", "--startup-file=no", str(folder / "task1.jl")],
    ]
    blocks = protocol.split("COMMAND: ")[1:]
    assert len(blocks) == len(commands)
    for command, block in zip(commands, blocks, strict=True):
        expected = block.split("STDOUT:\n", 1)[1].split("\nSTDERR:", 1)[0]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
        )
        assert result.returncode == 0, result.stderr
        assert result.stderr == "", result.stderr
        assert result.stdout.rstrip() == expected, result.stdout
    print(
        "OK: 8 fragments, 8 edge cases, 2 exact outputs, predictions unchanged"
    )


if __name__ == "__main__":
    main()
