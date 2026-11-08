def discount(amount: int, member: bool) -> int:
    if amount < 0:
        raise ValueError("amount must be nonnegative")
    if amount < 100:
        return 0
    rate = 20 if member else 10
    return min(amount * rate // 100, 500)
