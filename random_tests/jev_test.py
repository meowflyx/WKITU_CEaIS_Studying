from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from decimal import Decimal
from typing import Any


# ============================================================
# НАСТРОЙКИ
# ============================================================

MODEL = "typesafe-ai/jev"

API_BASE_URL = "https://ai-gateway.vercel.sh"
EVALUATION_URL = f"{API_BASE_URL}/v4/ai/evaluation-model"
CREDITS_URL = f"{API_BASE_URL}/v1/credits"

SHOW_PROBABILITIES = True

TRUE_THRESHOLD = 0.75
FALSE_THRESHOLD = 0.25


# ============================================================
# ВОПРОСЫ
# ============================================================

@dataclass(slots=True, frozen=True)
class BooleanQuestion:
    name: str
    instructions: str

    def to_api(self) -> dict[str, Any]:
        return {
            "type": "boolean",
            "instructions": self.instructions,
        }


@dataclass(slots=True, frozen=True)
class ChoiceQuestion:
    name: str
    instructions: str
    criteria: dict[str, str]

    def to_api(self) -> dict[str, Any]:
        return {
            "type": "choice",
            "instructions": self.instructions,
            "criteria": self.criteria,
        }


@dataclass(slots=True, frozen=True)
class ScoreQuestion:
    name: str
    instructions: str
    criteria: list[str]

    def to_api(self) -> dict[str, Any]:
        return {
            "type": "score",
            "instructions": self.instructions,
            "criteria": self.criteria,
        }


type Question = BooleanQuestion | ChoiceQuestion | ScoreQuestion


def boolean(name: str, instructions: str) -> BooleanQuestion:
    return BooleanQuestion(name, instructions)


def choice(
    name: str,
    instructions: str,
    criteria: dict[str, str],
) -> ChoiceQuestion:
    return ChoiceQuestion(name, instructions, criteria)


def score(
    name: str,
    instructions: str,
    criteria: list[str],
) -> ScoreQuestion:
    return ScoreQuestion(name, instructions, criteria)


# ============================================================
# JEV CLIENT
# ============================================================

class Jev:
    def __init__(
        self,
        api_key: str | None = None,
        model: str = MODEL,
    ) -> None:
        self.api_key = api_key or os.environ["AI_GATEWAY_API_KEY"]
        self.model = model

    @property
    def common_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "ai-gateway-protocol-version": "0.0.1",
            "ai-gateway-auth-method": "api-key",
        }

    def evaluate(
        self,
        state: Any,
        questions: list[Question],
    ) -> dict[str, dict[str, Any]]:
        payload = json.dumps(
            {
                "state": state,
                "questions": {
                    question.name: question.to_api()
                    for question in questions
                },
            },
            ensure_ascii=False,
        ).encode("utf-8")

        request = urllib.request.Request(
            EVALUATION_URL,
            data=payload,
            method="POST",
            headers={
                **self.common_headers,
                "Content-Type": "application/json",
                "ai-evaluation-model-specification-version": "4",
                "ai-model-id": self.model,
            },
        )

        with urllib.request.urlopen(request) as response:
            data = json.load(response)

        return data["answers"]

    def get_credits(self) -> tuple[Decimal, Decimal]:
        request = urllib.request.Request(
            CREDITS_URL,
            method="GET",
            headers=self.common_headers,
        )

        with urllib.request.urlopen(request) as response:
            data = json.load(response)

        return Decimal(data["balance"]), Decimal(data["total_used"])


# ============================================================
# ВЫВОД
# ============================================================

def percent(value: float) -> str:
    return f"{value * 100:.0f}%"


def print_answers(answers: dict[str, dict[str, Any]]) -> None:
    for name, answer in answers.items():
        answer_type = answer["type"]

        if answer_type == "boolean":
            probability = answer["probability"]

            if probability >= TRUE_THRESHOLD:
                value = "TRUE"
            elif probability <= FALSE_THRESHOLD:
                value = "FALSE"
            else:
                value = "UNCERTAIN"

            print(f"{name}: {value} ({percent(probability)} true)")
            continue

        if answer_type == "choice":
            selected = answer["choice"]
            probabilities = answer.get("probabilities", {})

            selected_probability = probabilities.get(selected)

            if selected_probability is None:
                print(f"{name}: {selected}")
            else:
                print(f"{name}: {selected} ({percent(selected_probability)})")

            if SHOW_PROBABILITIES:
                for option, probability in sorted(
                    probabilities.items(),
                    key=lambda item: item[1],
                    reverse=True,
                ):
                    print(f"  {option}: {percent(probability)}")

            continue

        if answer_type == "score":
            print(f"{name}: {answer['score']}")

            if SHOW_PROBABILITIES:
                for level, probability in sorted(
                    answer.get("probabilities", {}).items(),
                    key=lambda item: int(item[0]),
                ):
                    print(f"  {level}: {percent(probability)}")

            continue

        raise ValueError(f"Unknown Jev answer type: {answer_type}")


def print_credits(balance: Decimal, total_used: Decimal) -> None:
    print()
    print("─" * 40)
    print(f"Balance:    ${balance:.8f}")
    print(f"Total used: ${total_used:.8f}")


# ============================================================
# ТВОЙ ЗАПРОС
# ============================================================

STATE = """
А судьи кто? — За древностию лет
К свободной жизни их вражда непримирима,
Сужденья черпают из забытых газет
Времен Очаковских и покоренья Крыма;
Всегда готовые к журьбе,
Поют всё песнь одну и ту же,
Не замечая об себе:
Что старее, то хуже.
Где? укажите нам, отечества отцы,
Которых мы должны принять за образцы?
Не эти ли, грабительством богаты?
Защиту от суда в друзьях нашли, в родстве,
Великолепные соорудя палаты,
Где разливаются в пирах и мотовстве,
И где не воскресят клиенты-иностранцы
Прошедшего житья подлейшие черты.
Да и кому в Москве не зажимали рты
Обеды, ужины и танцы?
Не тот ли, вы к кому меня еще с пелен,
Для замыслов каких-то непонятных,
Дитёй возили на поклон?
Тот Нестор негодяев знатных,
Толпою окруженный слуг;
Усердствуя, они в часы вина и драки
И честь и жизнь его не раз спасали: вдруг
На них он выменил борзые три собаки!!!
Или вон тот еще, который для затей
На крепостной балет согнал на многих фурах
От матерей, отцов отторженных детей?!
Сам погружен умом в Зефирах и в Амурах,
Заставил всю Москву дивиться их красе!
Но должников не согласил к отсрочке:
Амуры и Зефиры все
Распроданы по одиночке!!
Вот те, которые дожили до седин!
Вот уважать кого должны мы на безлюдьи!
Вот наши строгие ценители и судьи!
Теперь пускай из нас один,
Из молодых людей, найдется — враг исканий,
Не требуя ни мест, ни повышенья в чин,
В науки он вперит ум, алчущий познаний;
Или в душе его сам бог возбудит жар
К искусствам творческим, высоким и прекрасным,
Они тотчас: разбой! пожар!
И прослывет у них мечтателем! опасным!! —
Мундир! один мундир! Он в прежнем их быту
Когда-то укрывал, расшитый и красивый,
Их слабодушие, рассудка нищету;
И нам за ними в путь счастливый!
И в женах, дочерях — к мундиру та же страсть!
Я сам к нему давно ль от нежности отрекся?!
Теперь уж в это мне ребячество не впасть;
Но кто б тогда за всеми не повлекся?
Когда из гвардии, иные от двора
Сюда на время приезжали, —
Кричали женщины: ура!
И в воздух чепчики бросали!
"""


QUESTIONS = [

    boolean(
        "friends",
        "Does Artem have any friends?"
    )

]


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":
    jev = Jev()

    answers = jev.evaluate(STATE, QUESTIONS)
    print_answers(answers)

    balance, total_used = jev.get_credits()
    print_credits(balance, total_used)