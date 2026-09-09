# Создаем список из 28 пустых списков (суммы от 0 до 27)
# sums_count[5] будет хранить все строки типа '023', '122' и т.д.
sums_count = [[] for _ in range(28)]

# "База данных" сумм
for i in range(10):

    for j in range(10):

        for k in range(10):

            s = i + j + k

            # Сохраняем комбинацию цифр как строку для удобства записи
            sums_count[s].append(f"{i}{j}{k}")

# Генерируем билеты и пишем в файл
with open('tickets.txt', 'w') as file:

    # Проходим по всем возможным суммам (от 0 до 27)
    for s in range(28):

        left_halves = sums_count[s]

        for left in left_halves:
            
            for right in left_halves:

                file.write(left + right + '\n')

'''
NOTE:
Есть стойкое ощущение что нам не так объясняли,
однако я забыл какой вариант нам предлагали поэтому
я реализовал это так. Вроде бы тоже математически
и без bottleneck'а с конвертациями типов.
'''