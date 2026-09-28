"""Практика 4, задание 3: журнал редактора и цена копирования."""

const BLOCK_SIZE = 256
const LINE = "строка"
const EDIT = "вставка"

function insert_copy(lines::Vector{String}, index::Int, value::String)
    result = copy(lines)
    insert!(result, index, value)
    return result
end

function delete_copy(lines::Vector{String}, index::Int)
    result = copy(lines)
    deleteat!(result, index)
    return result
end

function make_shared(size::Int)
    size == 0 && return [String[]]
    return [fill(LINE, min(BLOCK_SIZE, size - start + 1))
            for start in 1:BLOCK_SIZE:size]
end

function insert_shared(blocks::Vector{Vector{String}}, index::Int, value::String)
    offset = index
    for number in eachindex(blocks)
        block = blocks[number]
        if offset <= length(block) + 1
            changed = insert_copy(block, offset, value)
            result = copy(blocks)
            if length(changed) <= BLOCK_SIZE
                result[number] = changed
            else
                result[number] = changed[1:128]
                insert!(result, number + 1, changed[129:end])
            end
            return result
        end
        offset -= length(block)
    end
    throw(BoundsError(blocks, index))
end

function delete_shared(blocks::Vector{Vector{String}}, index::Int)
    offset = index
    for number in eachindex(blocks)
        block = blocks[number]
        if offset <= length(block)
            changed = delete_copy(block, offset)
            result = copy(blocks)
            if isempty(changed) && length(blocks) > 1
                deleteat!(result, number)
            else
                result[number] = changed
            end
            return result
        end
        offset -= length(block)
    end
    throw(BoundsError(blocks, index))
end

function run_operations(style::Symbol, size::Int, count::Int=100_000)
    index = div(size, 2) + 1
    history = Any[]
    if style == :mutable
        lines = fill(LINE, size)
        for step in 1:count
            if isodd(step)
                insert!(lines, index, EDIT)
                push!(history, (:delete, index, LINE))
            else
                removed = splice!(lines, index)
                push!(history, (:insert, index, removed))
            end
            length(history) > 100 && popfirst!(history)
        end
        return length(lines)
    end

    state = style == :copy ? fill(LINE, size) : make_shared(size)
    insert = style == :copy ? insert_copy : insert_shared
    delete = style == :copy ? delete_copy : delete_shared
    for step in 1:count
        push!(history, state)
        length(history) > 100 && popfirst!(history)
        state = isodd(step) ? insert(state, index, EDIT) : delete(state, index)
    end
    return style == :copy ? length(state) : sum(length, state)
end

function measure(style::Symbol, size::Int)
    GC.gc()
    result = @timed run_operations(style, size)
    @assert result.value == size
    return result.time, result.bytes / 1024^3
end

function measure_undo(style::Symbol, size::Int=1_000)
    index = div(size, 2) + 1
    if style == :mutable
        lines = fill(LINE, size)
        for _ in 1:100
            insert!(lines, index, EDIT)
        end
        start = time_ns()
        for _ in 1:100
            deleteat!(lines, index)
        end
        elapsed = (time_ns() - start) / 1_000
        @assert lines == fill(LINE, size)
    else
        state = style == :copy ? fill(LINE, size) : make_shared(size)
        history = Any[state]
        insert = style == :copy ? insert_copy : insert_shared
        for _ in 1:100
            state = insert(state, index, EDIT)
            push!(history, state)
        end
        start = time_ns()
        state = history[1]
        elapsed = (time_ns() - start) / 1_000
        restored = style == :copy ? state : collect(Iterators.flatten(state))
        @assert restored == fill(LINE, size)
    end
    return elapsed
end

function threaded_run(style::Symbol, size::Int, reads_per_write::Int;
                      writes::Int=200)
    state = Ref{Any}(style == :mutable ? fill(LINE, size) : make_shared(size))
    guard = ReentrantLock()
    ready = Channel{Nothing}(4)
    start_together = Base.Event()
    index = div(size, 2) + 1
    counts = fill(div(reads_per_write * writes, 3), 3)
    for number in 1:rem(reads_per_write * writes, 3)
        counts[number] += 1
    end
    start = time_ns()
    writer = Threads.@spawn begin
        put!(ready, nothing)
        wait(start_together)
        for step in 1:writes
            lock(guard) do
                if style == :mutable
                    if isodd(step)
                        insert!(state[], index, EDIT)
                    else
                        deleteat!(state[], index)
                    end
                else
                    state[] = isodd(step) ? insert_shared(state[], index, EDIT) :
                        delete_shared(state[], index)
                end
            end
        end
    end
    readers = [Threads.@spawn begin
        put!(ready, nothing)
        wait(start_together)
        for _ in 1:count
            snapshot = lock(guard) do
                style == :mutable ? copy(state[]) : state[]
            end
            first_line = style == :mutable ? snapshot[1] : snapshot[1][1]
            @assert first_line == LINE
        end
    end for count in counts]
    for _ in 1:4
        take!(ready)
    end
    notify(start_together)
    fetch(writer)
    foreach(fetch, readers)
    return (time_ns() - start) / 1e9
end

function test_behavior()
    for size in (0, 1, 1_000)
        index = div(size, 2) + 1
        expected = fill(LINE, size)
        copied = copy(expected)
        shared = make_shared(size)
        old_copy = copied
        old_shared = shared
        insert!(expected, index, EDIT)
        copied = insert_copy(copied, index, EDIT)
        shared = insert_shared(shared, index, EDIT)
        @assert copied == expected
        @assert collect(Iterators.flatten(shared)) == expected
        size == 1_000 && @assert old_shared[1] === shared[1]
        @assert old_copy == fill(LINE, size)
        @assert collect(Iterators.flatten(old_shared)) == fill(LINE, size)
        deleteat!(expected, index)
        copied = delete_copy(copied, index)
        shared = delete_shared(shared, index)
        @assert copied == expected
        @assert collect(Iterators.flatten(shared)) == expected
    end
    for style in (:mutable, :copy, :shared)
        @assert run_operations(style, 1_000, 100) == 1_000
        @assert run_operations(style, 1_000, 1) == 1_001
        measure_undo(style)
    end
    empty = delete_shared(make_shared(1), 1)
    @assert insert_shared(empty, 1, EDIT) == [[EDIT]]
    for delete in (() -> deleteat!([LINE], 3),
                   () -> delete_copy([LINE], 3),
                   () -> delete_shared(make_shared(1), 3))
        try
            delete()
            error("Удаление вне документа не вызвало BoundsError")
        catch exception
            @assert exception isa BoundsError
        end
    end
end

function main()
    test_behavior()
    println("Проверка вставки, удаления, отката и 100 операций: OK")
    "--bench" in ARGS || return
    for size in (1_000, 1_000_000), style in (:mutable, :copy, :shared)
        seconds, allocated = measure(style, size)
        println("100000, $size, $style: $(round(seconds, digits=3)) c; ",
                "allocated $(round(allocated, digits=2)) GiB")
        flush(stdout)
    end
    for style in (:mutable, :copy, :shared)
        println("undo 100, $style: $(round(measure_undo(style), digits=1)) мкс")
    end
    for ratio in (0, 1, 2, 5, 10, 100), style in (:mutable, :shared)
        times = sort([threaded_run(style, 1_000, ratio; writes=10_000)
                      for _ in 1:3])
        println("threads, reads/write $ratio, $style: ",
                "$(round(times[2], digits=4)) c")
    end
end

main()
