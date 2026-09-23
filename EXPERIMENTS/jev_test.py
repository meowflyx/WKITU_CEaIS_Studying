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
                    question.name: question.to_api() for question in questions
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
Artem, also known as Omegalul, has zero friends. Everyone hates him.
For a reason, obviously. He's a bad person.
"""


QUESTIONS = [boolean("friends", "Does Artem have any friends?")]


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":
    jev = Jev()

    answers = jev.evaluate(STATE, QUESTIONS)
    print_answers(answers)

    balance, total_used = jev.get_credits()
    print_credits(balance, total_used)
