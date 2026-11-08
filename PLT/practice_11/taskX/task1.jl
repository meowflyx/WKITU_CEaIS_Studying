struct CatalogTimeout <: Exception end
Base.showerror(io::IO, ::CatalogTimeout) = print(io, "catalog: deadline exceeded")

function process(scenario::String)
    attempts = 0
    storage = Int[]
    status = "STOP"
    message = ""
    try
        scenario == "missing_file" && throw(SystemError("input.csv", 2))
        scenario == "empty" && throw(ArgumentError("file: empty"))
        quantity = scenario == "quantity" ? -1 : 2
        quantity < 1 && throw(ArgumentError("quantity: expected >= 1, got -1"))
        scenario == "capacity" && throw(OverflowError("rows: limit 100, got 101"))
        for attempt in 1:3
            attempts = attempt
            timedout = scenario == "timeout_always" ||
                       (scenario == "timeout_once" && attempt == 1)
            if timedout
                attempt == 3 && throw(CatalogTimeout())
                continue
            end
            scenario == "catalog_contract" &&
                throw(ArgumentError("catalog.code: required nonempty value"))
            break
        end
        total = scenario == "invariant" ? -1 : quantity * 100
        total < 0 && throw(DomainError(total, "internal invariant: total >= 0"))
        checkpoint = length(storage)
        try
            push!(storage, 1)
            scenario == "partial_save" && throw(Base.IOError("injected after first insert", 5))
            push!(storage, 2)
        catch error
            resize!(storage, checkpoint)
            rethrow()
        end
        status = scenario == "notify" ? "PARTIAL" : "OK"
        message = scenario == "notify" ? "notification unavailable; data saved" : ""
    catch error
        if error isa SystemError || error isa ArgumentError || error isa OverflowError ||
           error isa CatalogTimeout || error isa DomainError || error isa Base.IOError
            message = sprint(showerror, error)
        else
            rethrow()
        end
    end
    return (scenario, status, attempts, length(storage), message)
end

function main()
    scenarios = ["empty", "quantity", "missing_file", "timeout_once", "timeout_always",
                 "catalog_contract", "capacity", "invariant", "partial_save", "notify"]
    statuses = ["STOP", "STOP", "STOP", "OK", "STOP", "STOP", "STOP", "STOP", "STOP", "PARTIAL"]
    for (scenario, expected) in zip(scenarios, statuses)
        result = process(scenario)
        println(join(result, '\t'))
        @assert result[2] == expected
        @assert result[4] == (expected == "STOP" ? 0 : 2)
    end
    @assert process("timeout_once")[3] == 2
    @assert process("timeout_always")[3] == 3
    @assert process("normal")[2] == "OK"
    println("JULIA_OK: 10 failures, retry limit, normal case")
end

main()
