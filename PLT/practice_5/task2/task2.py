import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path
from threading import RLock
from typing import NamedTuple, Protocol


class Document(NamedTuple):
    value: str
    version: int


class Storage(Protocol):
    def save(self, key: str, value: str) -> int:
        ...

    def get(self, key: str) -> Document | None:
        ...

    def delete(self, key: str) -> bool:
        ...

    def keys(self, prefix: str = "") -> list[str]:
        ...

    def replace(self, key: str, version: int, value: str) -> bool:
        ...


def check_key(key: str) -> None:
    if not isinstance(key, str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", key
    ):
        raise ValueError("Invalid key")
    reserved = {"CON", "PRN", "AUX", "NUL"}
    reserved.update(f"COM{i}" for i in range(1, 10))
    reserved.update(f"LPT{i}" for i in range(1, 10))
    if key.split(".")[0].upper() in reserved or key.endswith("."):
        raise ValueError("Invalid key")


def check_prefix(prefix: str) -> None:
    if not isinstance(prefix, str) or not re.fullmatch(
        r"[A-Za-z0-9_.-]{0,64}", prefix
    ):
        raise ValueError("Invalid prefix")


def check_value(value: str) -> None:
    if not isinstance(value, str):
        raise TypeError("Value must be str")


def check_version(version: int) -> None:
    if type(version) is not int or not 1 <= version < 2**63:
        raise ValueError("Invalid version")


class MemoryStore:

    def __init__(self):
        self.lock = RLock()
        self.state = {"clock": 0, "documents": {}}

    def _load(self):
        return self.state

    def _commit(self, state):
        self.state = state

    def save(self, key: str, value: str) -> int:
        check_key(key)
        check_value(value)
        with self.lock:
            state = self._load()
            state["clock"] += 1
            state["documents"][key] = [value, state["clock"]]
            self._commit(state)
            return state["clock"]

    def get(self, key: str) -> Document | None:
        check_key(key)
        with self.lock:
            item = self._load()["documents"].get(key)
            return None if item is None else Document(*item)

    def delete(self, key: str) -> bool:
        check_key(key)
        with self.lock:
            state = self._load()
            if key not in state["documents"]:
                return False
            del state["documents"][key]
            self._commit(state)
            return True

    def keys(self, prefix: str = "") -> list[str]:
        check_prefix(prefix)
        with self.lock:
            return [
                key for key in self._load()["documents"]
                if key.startswith(prefix)
            ]

    def replace(self, key: str, version: int, value: str) -> bool:
        check_key(key)
        check_version(version)
        check_value(value)
        with self.lock:
            state = self._load()
            item = state["documents"].get(key)
            if item is None or item[1] != version:
                return False
            state["clock"] += 1
            state["documents"][key] = [value, state["clock"]]
            self._commit(state)
            return True


class FileStore(MemoryStore):
    def __init__(self, path: Path):
        super().__init__()
        self.path = path
        if not path.exists():
            self._commit(self.state)

    def _load(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _commit(self, state):
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(state, ensure_ascii=False), encoding="utf-8"
        )
        # сначала записываем целый файл, затем заменяем прежний
        temporary.replace(self.path)


class SQLiteStore:

    def __init__(self, path: Path):
        self.path = path
        with closing(self._connect()) as connection, connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS documents "
                "(key TEXT PRIMARY KEY, value TEXT NOT NULL, "
                "version INTEGER NOT NULL)"
            )
            connection.execute(
                "CREATE TABLE IF NOT EXISTS counter "
                "(id INTEGER PRIMARY KEY CHECK(id = 1), "
                "version INTEGER NOT NULL)"
            )
            connection.execute("INSERT OR IGNORE INTO counter VALUES (1, 0)")

    def _connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def _next_version(self, connection):
        connection.execute(
            "UPDATE counter SET version = version + 1 WHERE id = 1"
        )
        return connection.execute(
            "SELECT version FROM counter WHERE id = 1"
        ).fetchone()[0]

    def save(self, key: str, value: str) -> int:
        check_key(key)
        check_value(value)
        with closing(self._connect()) as connection, connection:
            connection.execute("BEGIN IMMEDIATE")
            version = self._next_version(connection)
            connection.execute(
                "INSERT INTO documents VALUES (?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET "
                "value = excluded.value, version = excluded.version",
                (key, value, version),
            )
            return version

    def get(self, key: str) -> Document | None:
        check_key(key)
        with closing(self._connect()) as connection:
            item = connection.execute(
                "SELECT value, version FROM documents WHERE key = ?", (key,)
            ).fetchone()
            return None if item is None else Document(*item)

    def delete(self, key: str) -> bool:
        check_key(key)
        with closing(self._connect()) as connection, connection:
            return connection.execute(
                "DELETE FROM documents WHERE key = ?", (key,)
            ).rowcount == 1

    def keys(self, prefix: str = "") -> list[str]:
        check_prefix(prefix)
        with closing(self._connect()) as connection:
            return [row[0] for row in connection.execute(
                "SELECT key FROM documents "
                "WHERE substr(key, 1, length(?)) = ?",
                (prefix, prefix),
            )]

    def replace(self, key: str, version: int, value: str) -> bool:
        check_key(key)
        check_version(version)
        check_value(value)
        with closing(self._connect()) as connection, connection:
            connection.execute("BEGIN IMMEDIATE")
            item = connection.execute(
                "SELECT version FROM documents WHERE key = ?", (key,)
            ).fetchone()
            if item is None or item[0] != version:
                return False
            latest = self._next_version(connection)
            return connection.execute(
                "UPDATE documents SET value = ?, version = ? "
                "WHERE key = ? AND version = ?",
                (value, latest, key, version),
            ).rowcount == 1


class CachedStore:

    def __init__(self, storage: Storage):
        self.storage = storage
        self.cache = {}
        self.lock = RLock()

    def get(self, key: str) -> Document | None:
        check_key(key)
        with self.lock:
            if key not in self.cache:
                self.cache[key] = self.storage.get(key)
            return self.cache[key]

    def save(self, key: str, value: str) -> int:
        with self.lock:
            version = self.storage.save(key, value)
            self.cache.pop(key, None)
            return version

    def delete(self, key: str) -> bool:
        with self.lock:
            deleted = self.storage.delete(key)
            self.cache.pop(key, None)
            return deleted

    def keys(self, prefix: str = "") -> list[str]:
        return self.storage.keys(prefix)

    def replace(self, key: str, version: int, value: str) -> bool:
        with self.lock:
            replaced = self.storage.replace(key, version, value)
            self.cache.pop(key, None)
            return replaced


class ValidatedCache(CachedStore):
    def get(self, key: str) -> Document | None:
        with self.lock:
            current = self.storage.get(key)
            if current is None:
                self.cache.pop(key, None)
                return None
            cached = self.cache.get(key)
            if cached is None or cached.version != current.version:
                self.cache[key] = current
            return self.cache[key]
