from typing import cast, Optional

user: Optional[str] = None
# Вводим явное приведение типа, чтобы обойти проверку mypy
forced_user = cast(str, user) 

print(forced_user.upper())    # mypy МОЛЧИТ, но в runtime получаем AttributeError