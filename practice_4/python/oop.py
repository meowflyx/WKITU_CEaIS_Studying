from collections import Counter
from models import Event, UserStats

class UserHistory:
    def __init__(self, user_id: str) -> None:
        self._user_id = user_id
        self._events: list[Event] = []

    def add_event(self, event: Event) -> None:
        self._events.append(event)

    def calculate_stats(self) -> UserStats:
        if not self._events:
            return UserStats(self._user_id, 0, 0, None)
        
        sorted_evs = sorted(self._events, key=lambda e: e.timestamp)
        return UserStats(
            user_id=self._user_id,
            session_count=self._count_sessions(sorted_evs),
            total_duration=sum(e.duration for e in sorted_evs),
            most_frequent_event_type=self._find_most_frequent(sorted_evs)
        )

    def _count_sessions(self, sorted_events: list[Event]) -> int:
        count = 0
        last_ts: int | None = None
        for ev in sorted_events:
            if last_ts is None or (ev.timestamp - last_ts > 1800):
                count += 1
            last_ts = ev.timestamp
        return count

    def _find_most_frequent(self, events: list[Event]) -> str | None:
        counts = Counter(e.event_type for e in events)
        if not counts:
            return None
        return min(counts.keys(), key=lambda k: (-counts[k], k))

class EventLogProcessor:
    def __init__(self, events: list[Event]) -> None:
        self._histories: dict[str, UserHistory] = {}
        for ev in events:
            if ev.user_id not in self._histories:
                self._histories[ev.user_id] = UserHistory(ev.user_id)
            self._histories[ev.user_id].add_event(ev)

    def process_all(self) -> dict[str, UserStats]:
        return {uid: h.calculate_stats() for uid, h in self._histories.items()}

def process_oop(events: list[Event]) -> dict[str, UserStats]:
    return EventLogProcessor(events).process_all()