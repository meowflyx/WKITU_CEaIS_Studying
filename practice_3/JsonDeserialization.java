// Класс-модель
class UserDto {
    public String email; // Ожидается non-null строка
}

// При разборе '{"name": "Alice"}' Jackson запишет в field email значение null
UserDto user = objectMapper.readValue(jsonStr, UserDto.class);
System.out.println(user.email.toUpperCase()); // NullPointerException во время исполнения!