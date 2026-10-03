import java.util.*;
import java.util.stream.Collectors;

class Functional {

    private record SessionAcc(int count, Long lastTs) {}

    public static Map<String, UserStats> processFunctional(List<Event> events) {
        return events.stream()
                .sorted(Comparator.comparingLong(Event::timestamp))
                .collect(Collectors.groupingBy(Event::userId))
                .entrySet().stream()
                .collect(Collectors.toMap(
                        Map.Entry::getKey,
                        e -> computeUserStatsFunctional(e.getKey(), e.getValue())
                ));
    }

    private static UserStats computeUserStatsFunctional(String userId, List<Event> sortedEvents) {
        var sessionResult = sortedEvents.stream().reduce(
                new SessionAcc(0, null),
                (acc, ev) -> (acc.lastTs() == null || (ev.timestamp() - acc.lastTs() > 1800))
                        ? new SessionAcc(acc.count() + 1, ev.timestamp())
                        : new SessionAcc(acc.count(), ev.timestamp()),
                (a1, a2) -> a1
        );

        String mostFreq = sortedEvents.stream()
                .collect(Collectors.groupingBy(Event::eventType, Collectors.counting()))
                .entrySet().stream()
                .min((e1, e2) -> {
                    int cmp = Long.compare(e2.getValue(), e1.getValue());
                    return cmp != 0 ? cmp : e1.getKey().compareTo(e2.getKey());
                })
                .map(Map.Entry::getKey)
                .orElse(null);

        int totalDuration = sortedEvents.stream().mapToInt(Event::duration).sum();

        return new UserStats(userId, sessionResult.count(), totalDuration, mostFreq);
    }
}