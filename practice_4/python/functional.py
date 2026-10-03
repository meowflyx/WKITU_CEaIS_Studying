from functools import reduce
from models import Event, UserStats

def process_functional(events: list[Event]) -> dict[str, UserStats]:
    sorted_events = tuple(sorted(events, key=lambda e: e.timestamp))
    
    # Чистая группировка
    grouped = reduce(
        lambda acc, ev: {**acc, ev.user_id: acc.get(ev.user_id, ()) + (ev,)},
        sorted_events,
        {}
    )

    def compute_sessions(u_events: tuple[Event, ...]) -> int:
        return reduce(
            lambda acc, ev: (acc[0] + 1, ev.timestamp) if acc[1] is None or (ev.timestamp - acc[1] > 1800) else (acc[0], ev.timestamp),
            u_events,
            (0, None)
        )[0]

    def compute_most_frequent(u_events: tuple[Event, ...]) -> str | None:
        counts = reduce(
            lambda acc, e: {**acc, e.event_type: acc.get(e.event_type, 0) + 1},
            u_events,
            {}
        )
        return min(counts.keys(), key=lambda k: (-counts[k], k)) if counts else None

    return {
        uid: UserStats(
            user_id=uid,
            session_count=compute_sessions(evs),
            total_duration=sum(map(lambda e: e.duration, evs)),
            most_frequent_event_type=compute_most_frequent(evs)
        )
        for uid, evs in grouped.items()
    }