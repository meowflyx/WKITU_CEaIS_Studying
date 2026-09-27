from typing import Optional

def find_user(user_id: int) -> Optional[str]:
    users = {1: "Alice", 2: "Bob"}
    return users.get(user_id)

user = find_user(3)
# mypy выдаст ошибку: item "None" of "Optional[str]" has no attribute "upper"

if user is not None:
    print(user.upper())     # Защищено сужением типов mypy
