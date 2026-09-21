from dataclasses import dataclass
from datetime import date
from typing import TypeAlias, assert_never, final


@dataclass
class PassRequest:
    # хранит все поля вместе; допустимость проверяется после создания.

    state: str
    submitted_at: date | None = None
    approved_by: int | None = None
    valid_until: date | None = None
    rejection_reason: str | None = None

    def validate(self) -> None:
        # отклоняет пропущенные обязательные и запрещённые поля состояния.
        present = (
            self.submitted_at is not None,
            self.approved_by is not None,
            self.valid_until is not None,
            self.rejection_reason is not None,
        )
        match self.state:
            case "черновик":
                if any(present):
                    raise ValueError("Черновик содержит лишние данные")
            case "подана":
                if not present[0]:
                    raise ValueError("У поданной заявки нет даты подачи")
                if any(present[1:]):
                    raise ValueError("У поданной заявки есть лишние данные")
            case "одобрена":
                if not present[1]:
                    raise ValueError("У одобренной заявки нет утвердившего")
                if not present[2]:
                    raise ValueError("У одобренной заявки нет срока действия")
                if present[3]:
                    raise ValueError("У одобренной заявки есть причина отказа")
            case "отклонена":
                if not present[3]:
                    raise ValueError("У отклонённой заявки нет причины отказа")
                if present[2]:
                    raise ValueError("У отклонённой заявки есть срок действия")
                if present[1]:
                    raise ValueError("У отклонённой заявки есть утвердивший")
            case _:
                raise ValueError("Неизвестное состояние")


@final
@dataclass(frozen=True, slots=True)
class Draft:
    # черновик без данных о подаче и решении.
    pass


@final
@dataclass(frozen=True, slots=True)
class Submitted:
    # поданная заявка с обязательной датой подачи.

    submitted_at: date


@final
@dataclass(frozen=True, slots=True)
class Approved:
    # одобренная заявка с утвердившим и датой окончания действия.

    approved_by: int
    valid_until: date
    submitted_at: date | None = None


@final
@dataclass(frozen=True, slots=True)
class Rejected:
    # отказ с обязательной причиной; поля срока действия нет.

    rejection_reason: str
    submitted_at: date | None = None


Request: TypeAlias = Draft | Submitted | Approved | Rejected


def describe(request: Request) -> str:
    # разбирает все варианты; mypy проверяет полноту через assert_never.
    match request:
        case Draft():
            return "Состояние: черновик"
        case Submitted(submitted_at=submitted_at):
            return f"Состояние: подана. Дата подачи: {submitted_at}"
        case Approved(approved_by=approved_by, valid_until=valid_until):
            return (
                f"Состояние: одобрена. Утвердивший: {approved_by}. "
                f"Действует до: {valid_until}"
            )
        case Rejected(rejection_reason=reason):
            return f"Состояние: отклонена. Причина: {reason}"
    assert_never(request)


def can_enter(request: Request) -> bool:
    # проверяет разрешение по состоянию; проверка текущей даты вне задания.
    match request:
        case Draft() | Submitted() | Rejected():
            return False
        case Approved():
            return True
    assert_never(request)


def main() -> None:
    # выводит четыре допустимых варианта новой модели.
    requests: list[Request] = [
        Draft(),
        Submitted(date(2026, 9, 22)),
        Approved(123, date(2026, 12, 31)),
        Rejected("Неверные данные"),
    ]
    for request in requests:
        print(describe(request))


if __name__ == "__main__":
    main()
