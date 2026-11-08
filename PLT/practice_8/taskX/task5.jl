using Statistics
using Printf
function calculate(request::Tuple{Int,Int})
    identity, cost = request
    cost >= 0 || throw(ArgumentError("cost must be nonnegative"))
    state = mod(identity, 1_000_003)
    for _ in 1:cost
        state = mod(state * 33 + 17, 1_000_003)
    end
    state
end
direct(requests) = [calculate(request) for request in requests]
function cached(requests)
    cache = Dict{Tuple{Int,Int},Int}()
    [get!(() -> calculate(request), cache, request) for request in requests]
end
cache_allowed(requests) = !isempty(requests) &&
    length(Set(requests)) * 4 <= length(requests) && all(r -> r[2] >= 100, requests)
guarded(requests) = cache_allowed(requests) ? cached(requests) : direct(requests)
function main()
    datasets = [
        ("repeated_costly", fill((0, 1000), 1000)),
        ("unique_costly", [(index, 1000) for index in 0:999]),
        ("unique_cheap", [(index, 0) for index in 0:999]),
    ]
    for requests in [Tuple{Int,Int}[], [(0, 0)], [(2, 100), (2, 100)], [(typemax(Int), 1)]]
        @assert direct(requests) == cached(requests) == guarded(requests)
    end
    invalid = false
    try
        calculate((0, -1))
    catch error
        error isa ArgumentError || rethrow()
        invalid = true
    end
    @assert invalid
    open(joinpath(@__DIR__, "results_julia.csv"), "w") do file
        println(file, "dataset,method,trial,seconds")
        for (name, requests) in datasets
            reference = direct(requests)
            for method in (direct, cached, guarded, cache_allowed)
                for _ in 1:3
                    result = method(requests)
                    @assert result isa Bool || result == reference
                end
                times = Float64[]
                for trial in 1:7
                    started = time_ns()
                    result = method(requests)
                    elapsed = (time_ns()-started)/1e9
                    @assert result isa Bool || result == reference
                    push!(times, elapsed)
                    @printf(file, "%s,%s,%d,%.9f\n", name, string(method), trial, elapsed)
                end
                @printf("%s %s: median=%.9f min=%.9f max=%.9f\n",
                    name, string(method), median(times), minimum(times), maximum(times))
            end
        end
    end
    println("JULIA=", VERSION, " TRIALS=7 WARMUP=3 DATASETS=3 EDGE_CASES=5 OK")
end

main()
