def shout(func):

    def wrapper(*args, **kwargs):

        result = func(*args, **kwargs)

        return result.upper()
    
    return wrapper


@shout
def get_greeting(name):
    return f"Привет, {name}! Как дела?"


@shout
def get_farewell():
    return "До скорой встречи."


print(get_greeting("Андрей"))
print(get_farewell())      