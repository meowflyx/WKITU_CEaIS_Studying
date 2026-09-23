def outer():

   counter = 0

   def Collatz(N: int):

       result = int(N/2 if N%2==0 else 3*N + 1)

       nonlocal counter
       counter += 1

       print(result)

       if result == 1:
           # не просто завершаем, а возвращаем каунтер
           return counter

       # вместо простого рекусивного вызова функции добавляем return  
       else: return Collatz(result)

   return Collatz

if __name__ == "__main__":

   N = 8
   result = outer()(N)
   print(f'Потребовалось {result} шаг(-а, -ов)')
