import java.util.Map;
import java.util.Optional;

public class NullSafety {
    public static Optional<String> findUser(int userId) {
        Map<Integer, String> users = Map.of(1, "Alice", 2, "Bob");
        return Optional.ofNullable(users.get(userId));
    }

    public static void main(String[] args) {
        Optional<String> user = findUser(3);
        
        // Компилятор не даст вызвать методы String напрямую у Optional
        // user.toUpperCase(); // Ошибка компиляции: cannot find symbol
        
        user.ifPresent(u -> System.out.println(u.toUpperCase()));
    }
}