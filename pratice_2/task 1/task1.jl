using InteractiveUtils

numbers = [3, 6, 9]

function greatest_common_divisor(numbers::Vector{<:Integer})::Int
    isempty(numbers) && throw(ArgumentError("numbers must not be empty"))

    divisor = abs(numbers[1])
    for number in numbers[2:end]
        number = abs(number)
        while number != 0
            divisor, number = number, divisor % number
        end
    end

    return divisor
end

println(greatest_common_divisor(numbers))

# Инспекция сгенерированного кода для конкретного вызова:
# @code_lowered показывает Julia IR после понижения синтаксиса.
@code_lowered greatest_common_divisor(numbers)

# @code_typed показывает типизированный Julia IR и предполагаемый тип результата.
#@code_typed greatest_common_divisor(numbers)

# @code_llvm показывает LLVM IR (низкоуровневое промежуточное представление).
#@code_llvm greatest_common_divisor(numbers)

# @code_native показывает машинные инструкции текущей архитектуры.
#@code_native greatest_common_divisor(numbers)