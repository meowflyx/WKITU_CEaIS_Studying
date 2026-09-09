# Создаем файл записывающий результат в output.txt
with open("output.txt", "w", encoding="utf-8") as file:

    for i in range(1, 1000):

        for j in range(1, 1000):

            si = str(i).zfill(3)
            sj = str(j).zfill(3)

            if si == sj:

                # Записываем совпадающие значения в файл
                file.write(si + " " + sj + "\n")

'''
Таким образом, мы выводим элементы на главной диагонали матрицы,
где i и j совпадают. И в этом случае, мы не преобразовываем str
в int.

'''