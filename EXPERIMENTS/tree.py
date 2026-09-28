def print_tree(height: int = 3) -> None:
    if height <= 0 or height % 2 == 0:
        raise ValueError("height must be a positive odd number")

    for num in range(1, height + 1, 2):
        indent = (height - num) // 2
        print(f"{' ' * indent}{'#' * num}")

    trunk_height = max(1, height // 5)
    for _ in range(trunk_height):
        print(f"{' ' * (height // 2)}||")

    print(f"{' ' * (height // 2)}||🦔")  # копайлот помог с ёжиком спс ему


print_tree(21)
