records = [
    ("samsung", 100, 2),
    ("poco", 50, 5),
    ("iphone", 120, 1),
    ("samsung", 80, 1),
]

function total_by_id(records::Vector{Tuple{String, Int64, Int64}})::Vector{Tuple{String, Int64}}
    # В Dict ключом будет идентификатор товара, а значением - накопленная
    # стоимость всех записей с этим идентификатором.
    totals = Dict{String, Int64}()

    for (identifier, price, quantity) in records
        # Если идентификатор встретился впервые, get возвращает 0.
        # Если он уже был, get возвращает накопленную сумму, и к ней
        # добавляется стоимость текущей записи.
        totals[identifier] = get(totals, identifier, 0) + price * quantity
    end

    # Dict не обязан хранить элементы в нужном порядке, поэтому сначала
    # превращаем его в массив пар, а затем сортируем пары по второй части.
    # rev=true означает сортировку от большей суммы к меньшей.
    # Эту часть мне было тяжело понять со старта, поэтому здесь я воспользовался помощью Codex.
    sorted_totals = sort(collect(totals), by=pair -> pair[2], rev=true)

    # В Julia элементы Dict после collect имеют тип Pair (key => value).
    # Здесь явно превращаем их в обычные кортежи как в питоне, чтобы результат был
    # таким же по смыслу, как список кортежей в Python.
    return [(pair.first, pair.second) for pair in sorted_totals]
end

# Samsung встречается два раза, поэтому его сумма должна быть равна
# 100 * 2 + 80 * 1 = 280. Это простой ручной контроль результата.
println(total_by_id(records))
