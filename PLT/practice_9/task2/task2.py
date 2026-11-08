from pathlib import Path
from tempfile import TemporaryDirectory
import platform
import time
import tracemalloc


def count_stream(file):
    return sum(1 for line in file)


def count_all(file):
    data = file.read()
    return data.count(b'\n') + bool(data and not data.endswith(b'\n'))


def count_list(file):
    lines = list(line for line in file)
    return len(lines)


def measure(path, operation):
    tracemalloc.start()
    started = time.perf_counter()
    with path.open('rb') as file:
        result = operation(file)
    elapsed = time.perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, peak, elapsed


def main():
    print('Python:', platform.python_version(), platform.platform())
    print('Повторное вычисление:')
    calls = []

    def calculate(value):
        calls.append(value)
        return value * 2

    def sequence():
        return (calculate(value) for value in [1, 2, 3])

    print('Первый проход:', list(sequence()), 'вызовов:', len(calls))
    print('Второй проход:', list(sequence()), 'вызовов:', len(calls))
    calls.clear()
    saved = list(sequence())
    print('Список дважды:', saved, saved, 'вызовов:', len(calls))
    single_use = sequence()
    print('Один генератор:', list(single_use), list(single_use))

    print('Закрытый файл:')
    with TemporaryDirectory(dir=Path(__file__).parent) as directory:
        path = Path(directory) / 'data.bin'
        path.write_bytes(b'first\nsecond\n')
        with path.open('rb') as file:
            lines = (line for line in file)
        try:
            list(lines)
        except ValueError as error:
            print(type(error).__name__ + ':', error)
        with path.open('rb') as file:
            print('Внутри with:', list(line for line in file))

        print('Побочный эффект:')

        def show(value):
            print('вычислено', value)
            return value * 2

        values = (show(value) for value in [1, 2])
        print('генератор создан')
        print('результат:', list(values))

        print('Измерения:')
        line = b'a' * 4095 + b'\n'
        block = line * 256
        for blocks in (20, 2048):
            with path.open('wb') as file:
                for _ in range(blocks):
                    file.write(block)
            print('Размер файла:', path.stat().st_size, 'байт')
            for name, operation in [('поток', count_stream), ('read', count_all), ('list', count_list)]:
                result, peak, elapsed = measure(path, operation)
                print(f'{name}: строк={result}; пик={peak} байт; время={elapsed:.3f} с')


if __name__ == '__main__':
    main()
