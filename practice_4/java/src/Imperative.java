import java.util.*;

public class Imperative {
    public static Map<String, UserStats> processImperative(List<Event> events) {
        var sorted = new ArrayList<>(events);
        sorted.sort(Comparator.comparingLong(Event::timestamp));

        var userEventsMap = new HashMap<String, List<Event>>();
        for (var ev : sorted) {
            userEventsMap.computeIfAbsent(ev.userId(), k -> new ArrayList<>()).add(ev);
        }

        var results = new HashMap<String, UserStats>();
        for (var entry : userEventsMap.entrySet()) {
            var uid = entry.getKey();
            var uEvents = entry.getValue();

            int sessionCount = 0;
            int totalDuration = 0;
            var counts = new HashMap<String, Integer>();
            Long lastTs = null;

            for (var ev : uEvents) {
                totalDuration += ev.duration();
                counts.put(ev.eventType(), counts.getOrDefault(ev.eventType(), 0) + 1);

                if (lastTs == null || (ev.timestamp() - lastTs > 1800)) {
                    sessionCount++;
                }
                lastTs = ev.timestamp();
            }

            String mostFreq = counts.entrySet().stream()
                    .min((e1, e2) -> {
                        int cmp = Integer.compare(e2.getValue(), e1.getValue());
                        return cmp != 0 ? cmp : e1.getKey().compareTo(e2.getKey());
                    })
                    .map(Map.Entry::getKey)
                    .orElse(null);

            results.put(uid, new UserStats(uid, sessionCount, totalDuration, mostFreq));
        }
        return results;
    }
}