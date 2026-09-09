def outer():


   counter = 0


   def Collatz(N: int):

    
       result = int(N/2 if N%2==0 else 3*N + 1)

        # Используем nonlocal для доступа к переменной counter
       nonlocal counter
       counter += 1


       print(result)

        # Возвращаем результат, если он равен 1, иначе продолжаем рекурсию
       if result == 1:
           return counter
       else:
           return Collatz(result)


   return Collatz


if __name__ == "__main__":

   N = 8
   result = outer()(N)
   print(f'Потребовалось {result} шаг(-а, -ов)')

   '''
   Теперь мы можем вызвать функцию Collatz с любым числом, 
   и она будет выводить количество шагов, необходимых для достижения 1.
   '''
