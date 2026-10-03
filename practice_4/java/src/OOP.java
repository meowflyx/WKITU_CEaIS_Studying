import java.util.*;
import java.util.stream.Collectors;

public class OOP {

    public static class UserHistory {
        private final String userId;
        private final List<Event> events = new ArrayList<>();

        public UserHistory(String userId) {
            this.userId = userId;
        }

        public void addEvent(Event ev) {
            this.events.add(ev);
        }

        public UserStats calculateStats() {
            if (events.isEmpty()) {
                return new UserStats(userId, 0, 0, null);
            }
            var sorted = events.stream()
                    .sorted(Comparator.comparingLong(Event::timestamp))
                    .toList(); // Метод .toList() доступен с Java 16+

            return new UserStats(
                userId,
                countSessions(sorted),
                sorted.stream().mapToInt(Event::duration).sum(),
                findMostFrequent(sorted)
            );
        }

        private int countSessions(List<Event> sorted) {
            int count = 0;
            Long lastTs = null;
            for (var ev : sorted) {
                if (lastTs == null || (ev.timestamp() - lastTs > 1800)) {
                    count++;
                }
                lastTs = ev.timestamp();
            }
            return count;
        }

        private String findMostFrequent(List<Event> sorted) {
            return sorted.stream()
                    .collect(Collectors.groupingBy(Event::eventType, Collectors.counting()))
                    .entrySet().stream()
                    .min((e1, e2) -> {
                        int cmp = Long.compare(e2.getValue(), e1.getValue());
                        return cmp != 0 ? cmp : e1.getKey().compareTo(e2.getKey());
                    })
                    .map(Map.Entry::getKey)
                    .orElse(null);
        }
    }

    public static class EventLogProcessor {
        private final Map<String, UserHistory> histories = new HashMap<>();

        public EventLogProcessor(List<Event> events) {
            events.forEach(ev -> histories.computeIfAbsent(ev.userId(), UserHistory::new).addEvent(ev));
        }

        public Map<String, UserStats> processAll() {
            var res = new HashMap<String, UserStats>();
            histories.forEach((k, v) -> res.put(k, v.calculateStats()));
            return res;
        }
    }

    public static Map<String, UserStats> processOOP(List<Event> events) {
        return new EventLogProcessor(events).processAll();
    }
}