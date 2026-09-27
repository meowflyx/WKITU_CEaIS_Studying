List<Optional<Double>> salaries = List.of(
    Optional.of(1000.0),
    Optional.empty(), // Данные скрыты
    Optional.of(2000.0)
);

// Ошибка бизнес-логики: отсутствие ответа интерпретируется как 0
double average = salaries.stream()
    .mapToDouble(s -> s.orElse(0.0))
    .average()
    .orElse(0.0); // Результат: 1000.0 вместо 1500.0