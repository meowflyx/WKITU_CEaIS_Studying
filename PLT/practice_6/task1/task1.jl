"""Изменяемая точка с одним целочисленным полем."""
mutable struct MutablePoint
    x::Int
end

"""Неизменяемая точка с одним целочисленным полем."""
struct Point
    x::Int
end

"""Неизменяемая оболочка над изменяемым вектором."""
struct Box
    items::Vector{Int}
end

"""Показать общую ссылку при присваивании изменяемой структуры."""
function mutable_assignment()
    println("J1")
    original = MutablePoint(10)
    alias = original
    alias.x = 20
    println("original: ", original.x)
    println("alias: ", alias.x)
    println("same: ", original === alias)
    @assert original.x == 20 && original === alias
end

"""Отделить запрет изменения поля от разрешенной перепривязки имени."""
function immutable_assignment()
    println("J2")
    original = Point(10)
    alias = original
    caught = false
    try
        alias.x = 20
    catch error
        error isa ErrorException || rethrow()
        caught = true
        println(sprint(showerror, error))
    end
    alias = Point(20)
    println("original: ", original.x)
    println("rebound: ", alias.x)
    @assert caught && original.x == 10 && alias.x == 20
end

"""Проверить, что неизменяемая оболочка не замораживает вектор."""
function immutable_container()
    println("J3")
    original = Box([1])
    alias = original
    push!(alias.items, 2)
    println("items: ", original.items)
    println("same vector: ", original.items === alias.items)
    caught = false
    try
        alias.items = [99]
    catch error
        error isa ErrorException || rethrow()
        caught = true
        println(sprint(showerror, error))
    end
    @assert caught && original.items == [1, 2]
end

"""Сравнить поверхностные копии массивов значений и изменяемых объектов."""
function array_copy()
    println("J4")
    values = [Point(1)]
    values_copy = copy(values)
    values_copy[1] = Point(9)
    objects = [MutablePoint(1)]
    objects_copy = copy(objects)
    objects_copy[1].x = 9
    println("values: ", values[1].x, " ", values_copy[1].x)
    println("objects: ", objects[1].x, " ", objects_copy[1].x)
    println("same arrays: ", objects === objects_copy)
    println("same object: ", objects[1] === objects_copy[1])
    @assert values[1].x == 1 && values_copy[1].x == 9
    @assert objects[1].x == 9 && objects[1] === objects_copy[1]
    @assert objects !== objects_copy
end

"""Проверить пустой массив, границу Int и два неверных обращения."""
function edge_cases()
    empty = Int[]
    @assert copy(empty) == empty && copy(empty) !== empty
    maximum = typemax(Int)
    @assert copy([Point(maximum)])[1].x == maximum
    caught_index = false
    try
        empty[1]
    catch error
        error isa BoundsError || rethrow()
        caught_index = true
    end
    caught_type = false
    try
        Point("bad")
    catch error
        error isa MethodError || rethrow()
        caught_type = true
    end
    @assert caught_index && caught_type
    println("Julia edge cases: 4/4 OK")
end

mutable_assignment()
immutable_assignment()
immutable_container()
array_copy()
println("Julia: 4/4 OK")
edge_cases()
