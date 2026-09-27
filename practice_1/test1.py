def aggregate_costs(records: list) -> list[tuple]:
  totals = {}
  for item_id, price, quantity in records:
    totals[item_id] = totals.get(item_id, 0.0) + price * quantity
  return sorted(totals.items(), key=lambda x: x[1], reverse=True)