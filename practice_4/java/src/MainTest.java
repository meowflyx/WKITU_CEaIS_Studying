import java.util.*;

public class MainTest {

    public static void main(String[] args) {
        System.out.println("=== Запуск 8 тестов для Java-реализаций ===");

        // 1. Подготовка 8 тестовых наборов
        Map<String, List<Event>> testCases = new LinkedHashMap<>();

        // Тест 1: Пустой журнал
        testCases.put("1. Пустой журнал", List.of());

        // Тест 2: Один пользователь
        testCases.put("2. Один пользователь", List.of(
                new Event(100, "u1", "login", 10),
                new Event(200, "u1", "click", 5)
        ));

        // Тест 3: Граница 30 минут (1800 секунд)
        testCases.put("3. Граница 30 минут (1800с)", List.of(
                new Event(0, "u1", "view", 5),
                new Event(1800, "u1", "view", 5), // <= 1800s -> тот же сеанс
                new Event(3601, "u1", "view", 5)  // > 1800s -> новый сеанс
        ));

        // Тест 4: События с нулевой длительностью
        testCases.put("4. События с нулевой длительностью", List.of(
                new Event(100, "u1", "ping", 0),
                new Event(200, "u1", "ping", 0)
        ));

        // Тест 5: Неупорядоченный по времени журнал
        testCases.put("5. Неупорядоченный журнал", List.of(
                new Event(5000, "u1", "logout", 10),
                new Event(100, "u1", "login", 10),
                new Event(200, "u1", "click", 10)
        ));

        // Тест 6: Множественные сеансы
        testCases.put("6. Множественные сеансы", List.of(
                new Event(0, "u1", "a", 10),
                new Event(2000, "u1", "b", 10),
                new Event(5000, "u1", "a", 10)
        ));

        // Тест 7: Несколько пользователей
        testCases.put("7. Несколько пользователей", List.of(
                new Event(100, "u1", "click", 10),
                new Event(100, "u2", "view", 20)
        ));

        // Тест 8: Равные частоты типов
        testCases.put("8. Равные частоты типов", List.of(
                new Event(100, "u1", "b_type", 10),
                new Event(200, "u1", "a_type", 10)
        ));

        // 2. Выполнение и сверка результатов всех реализаций
        int passed = 0;
        for (var entry : testCases.entrySet()) {
            String testName = entry.getKey();
            List<Event> events = entry.getValue();

            Map<String, UserStats> resImperative = Imperative.processImperative(events);
            Map<String, UserStats> resOOP = OOP.processOOP(events);
            Map<String, UserStats> resFunctional = Functional.processFunctional(events);

            if (resImperative.equals(resOOP) && resOOP.equals(resFunctional)) {
                System.out.println("[OK] " + testName);
                passed++;
            } else {
                System.err.println("[FAIL] Ошибка на тесте: " + testName);
                System.err.println("  Imperative: " + resImperative);
                System.err.println("  OOP:        " + resOOP);
                System.err.println("  Functional: " + resFunctional);
            }
        }

        System.out.println("==========================================");
        System.out.println("Результат: " + passed + " из " + testCases.size() + " тестов успешно пройдены!");
    }
}