from models import Event, UserStats

def process_imperative(events: list[Event]) -> dict[str, UserStats]:
    sorted_events = sorted(events, key=lambda x: x.timestamp)
    user_events: dict[str, list[Event]] = {}
    
    for ev in sorted_events:
        if ev.user_id not in user_events:
            user_events[ev.user_id] = []
        user_events[ev.user_id].append(ev)
        
    results: dict[str, UserStats] = {}
    for uid, u_events in user_events.items():
        session_count = 0
        total_duration = 0
        event_type_counts: dict[str, int] = {}
        last_ts: int | None = None
        
        for ev in u_events:
            total_duration += ev.duration
            event_type_counts[ev.event_type] = event_type_counts.get(ev.event_type, 0) + 1
            if last_ts is None or (ev.timestamp - last_ts > 1800):
                session_count += 1
            last_ts = ev.timestamp
            
        most_freq = min(event_type_counts.keys(), key=lambda k: (-event_type_counts[k], k)) if event_type_counts else None
        results[uid] = UserStats(uid, session_count, total_duration, most_freq)
        
    return results