import json
from typing import Dict

# JSON не содержит обязательного поля "email"
raw_json = '{"id": 1, "name": "Alice"}'
data: Dict[str, str] = json.loads(raw_json)

# mypy молчит (data['email'] имеет тип Any под капотом, интерпретируемый как str)
email: str = data.get("email")  # На самом деле None
print(email.upper())    # AttributeError во время исполнения