using Dates

# наивная заявка с общим набором необязательных полей.
Base.@kwdef struct PassRequest
    state::String
    submitted_at::Union{Date, Nothing} = nothing
    approved_by::Union{Int, Nothing} = nothing
    valid_until::Union{Date, Nothing} = nothing
    rejection_reason::Union{String, Nothing} = nothing
end

# проверяет обязательные и запрещённые поля уже созданной заявки.
function validate(request::PassRequest)
    present = .!isnothing.((request.submitted_at, request.approved_by,
                            request.valid_until, request.rejection_reason))
    if request.state == "черновик"
        any(present) && throw(ArgumentError("Черновик содержит лишние данные"))
    elseif request.state == "подана"
        present[1] || throw(ArgumentError("У поданной заявки нет даты подачи"))
        any(present[2:4]) && throw(ArgumentError("У поданной заявки есть лишние данные"))
    elseif request.state == "одобрена"
        present[2] || throw(ArgumentError("У одобренной заявки нет утвердившего"))
        present[3] || throw(ArgumentError("У одобренной заявки нет срока действия"))
        present[4] && throw(ArgumentError("У одобренной заявки есть причина отказа"))
    elseif request.state == "отклонена"
        present[4] || throw(ArgumentError("У отклонённой заявки нет причины отказа"))
        present[3] && throw(ArgumentError("У отклонённой заявки есть срок действия"))
        present[2] && throw(ArgumentError("У отклонённой заявки есть утвердивший"))
    else
        throw(ArgumentError("Неизвестное состояние"))
    end
    return nothing
end

# общее семейство заявок; экземпляр абстрактного типа создать нельзя.
abstract type Request end

# черновик без полей подачи и решения.
struct Draft <: Request end

# поданная заявка обязательно содержит дату подачи.
struct Submitted <: Request
    submitted_at::Date
end

# одобренная заявка содержит сотрудника и дату окончания действия.
struct Approved <: Request
    approved_by::Int
    valid_until::Date
    submitted_at::Union{Date, Nothing}
end

Approved(approved_by::Int, valid_until::Date) =
    Approved(approved_by, valid_until, nothing)

# отклонённая заявка содержит причину; поля срока действия нет.
struct Rejected <: Request
    rejection_reason::String
    submitted_at::Union{Date, Nothing}
end

Rejected(rejection_reason::String) = Rejected(rejection_reason, nothing)

# описывает заявку методом, выбранным по конкретному типу аргумента.
describe(::Draft) = "Состояние: черновик"
describe(request::Submitted) = "Состояние: подана. Дата подачи: $(request.submitted_at)"
describe(request::Approved) =
    "Состояние: одобрена. Утвердивший: $(request.approved_by). Действует до: $(request.valid_until)"
describe(request::Rejected) = "Состояние: отклонена. Причина: $(request.rejection_reason)"

# проверяет разрешение по состоянию, без проверки текущей даты.
can_enter(::Draft) = false
can_enter(::Submitted) = false
can_enter(::Approved) = true
can_enter(::Rejected) = false

# выводит четыре допустимых варианта новой модели.
function main()
    requests = (Draft(), Submitted(Date(2026, 9, 22)),
                Approved(123, Date(2026, 12, 31)), Rejected("Неверные данные"))
    for request in requests
        println(describe(request))
    end
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
