from dataclasses import dataclass

@dataclass(frozen=True)
class Event:
    timestamp: int      # В секундах
    user_id: str
    event_type: str
    duration: int       # В секундах

@dataclass(frozen=True)
class UserStats:
    user_id: str
    session_count: int
    total_duration: int
    most_frequent_event_type: str | None  # Без Optional!