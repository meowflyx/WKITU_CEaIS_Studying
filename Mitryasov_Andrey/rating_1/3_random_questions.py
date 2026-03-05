import random
import json

#  меняй!
questions_directory = "Mitryasov_Andrey\\rating_1\\questions.json"

with open(questions_directory, "r", encoding="UTF-8") as file:
    questions_json = json.load(file)
    all_questions = questions_json["questions"]
    max_questions = len(all_questions)
    
    modifier_chance = 1
    modifiers = ["Замена вопроса", 
                 "Подсказка x1", 
                 "Отказаться от 1 вопроса", 
                 "+1 вопрос", 
                 "Помощь от друга"]
    
    chosen_modifier = random.choice(modifiers) if random.random() < modifier_chance else None
    if chosen_modifier:
        print(f"Вам выпал модификатор: {chosen_modifier}")

    while True:

        try:
            user_input = int(input(f"Введите количество вопросов (1-{max_questions}): "))

            if not (1 <= user_input <= max_questions):
                print(f"Введите число от 1 до {max_questions}!")
                continue
                
            amount_of_questions = user_input
            if chosen_modifier == "+1 вопрос":
                amount_of_questions = min(user_input + 1, max_questions)
            
            break

        except ValueError:
            print("Введите корректное целое число!")

    chosen_questions_data = random.sample(all_questions, amount_of_questions)
    chosen_questions = [q["question"] for q in chosen_questions_data]

print("--- Список вопросов ---")
for i, q in enumerate(chosen_questions, start=1):
    print(f"{i}. {q}")