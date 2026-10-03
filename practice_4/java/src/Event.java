public record Event(
    long timestamp,    // В секундах
    String userId,
    String eventType,
    int duration       // В секундах
) {}