public record UserStats(
    String userId,
    int sessionCount,
    int totalDuration,
    String mostFrequentEventType
) {}