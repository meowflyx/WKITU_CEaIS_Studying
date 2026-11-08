def discounted_price(amount: int, percent: int) -> int:
    """Проверить аргументы и округлить остаток цены до ближайшего целого.

    amount задаётся в минимальных денежных единицах, percent находится
    в диапазоне 0..100. Ровно половина округляется вверх.
    """
    if amount < 0 or not 0 <= percent <= 100:
        raise ValueError("amount >= 0 and 0 <= percent <= 100 required")
    return (amount * (100 - percent) + 50) // 100
