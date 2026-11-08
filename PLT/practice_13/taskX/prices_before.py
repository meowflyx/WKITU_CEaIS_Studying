def discounted_price(amount: int, percent: int) -> int:
    if amount < 0 or not 0 <= percent <= 100:
        raise ValueError("amount >= 0 and 0 <= percent <= 100 required")
    return round(amount * (100 - percent) / 100)
