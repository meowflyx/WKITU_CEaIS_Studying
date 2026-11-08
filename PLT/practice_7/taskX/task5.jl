using Statistics
using Printf
function histogram_run(size::Int, workers::Int, data::Vector{Int}=Vector{Int}(undef, max(size, 0)))
    size >= 0 || throw(ArgumentError("size must be nonnegative"))
    1 <= workers <= Threads.nthreads() || throw(ArgumentError("invalid workers"))
    length(data) == size || throw(ArgumentError("wrong buffer size"))
    started = time_ns()
    for i in eachindex(data)
        @inbounds data[i] = mod(i * 17, 256) + 1
    end
    prepared = time_ns()
    tasks = map(1:workers) do lane
        Threads.@spawn begin
            bins = zeros(Int, 256)
            first = fld((lane - 1) * size, workers) + 1
            last = fld(lane * size, workers)
            for index in first:last
                @inbounds bins[data[index]] += 1
            end
            bins
        end
    end
    partials = fetch.(tasks)
    counted = time_ns()
    merged = zeros(Int, 256)
    for bins in partials
        merged .+= bins
    end
    finished = time_ns()
    merged, (prepared-started)/1e9, (counted-prepared)/1e9,
        (finished-counted)/1e9, (finished-started)/1e9
end
@noinline function tick!(counters::Vector{Int}, index::Int)
    @inbounds counters[index] += 1
    nothing
end
@noinline local_tick(count::Int) = count + 1
function counters_run(workers::Int, iterations::Int, mode::Symbol)
    stride = mode == :padded ? 16 : 1
    counters = zeros(Int, workers * stride)
    @sync for lane in 1:workers
        Threads.@spawn begin
            index = 1 + (lane - 1) * stride
            if mode == :local
                count = 0
                for value in 1:iterations
                    count = local_tick(count)
                end
                counters[index] = count
            else
                for _ in 1:iterations
                    tick!(counters, index)
                end
            end
        end
    end
    expected = iterations
    @assert sum(counters) == workers * expected
    sum(counters)
end
function main()
    workers = Threads.nthreads()
    output = length(ARGS) == 1 ? ARGS[1] : joinpath(@__DIR__, "results.csv")
    size = 4_000_000
    data = Vector{Int}(undef, size)
    reference = histogram_run(size, 1, data)[1]
    for _ in 1:3
        @assert histogram_run(size, workers, data)[1] == reference
        for mode in (:adjacent, :padded, :local)
            counters_run(workers, 500_000, mode)
        end
    end
    @assert sum(histogram_run(0, workers)[1]) == 0
    @assert histogram_run(1, workers)[1][18] == 1
    invalid = false
    try
        histogram_run(-1, workers)
    catch error
        error isa ArgumentError || rethrow()
        invalid = true
    end
    @assert invalid
    header = !isfile(output)
    timings = Float64[]
    open(output, "a") do file
        header && println(file, "kind,workers,trial,prepare_s,count_s,merge_s,total_s,errors")
        for trial in 1:100
            bins, prepare, count, merge, total = histogram_run(size, workers, data)
            @assert bins == reference
            push!(timings, total)
            @printf(file, "histogram,%d,%d,%.9f,%.9f,%.9f,%.9f,0\n",
                workers, trial, prepare, count, merge, total)
            for mode in (:adjacent, :padded, :local)
                started = time_ns()
                result = counters_run(workers, 500_000, mode)
                elapsed = (time_ns()-started)/1e9
                @assert result > 0
                @printf(file, "%s,%d,%d,0,0,0,%.9f,0\n", mode, workers, trial, elapsed)
            end
        end
    end
    @printf("JULIA=%s WORKERS=%d TRIALS=100 MEDIAN=%.9f ERRORS=0 EDGE_CASES=3 OK\n",
        VERSION, workers, median(timings))
end

main()
