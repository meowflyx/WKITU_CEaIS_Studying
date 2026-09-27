function aggregate_costs(records)
    totals = Dict{Any, Float64}()
    for (id, price, quantity) in records
        totals[id] = get(totals, id, 0.0) + price * quantity
    end
    return sort([(k, v) for (k, v) in pairs(totals)], by = x -> x[2], rev = true)
end
