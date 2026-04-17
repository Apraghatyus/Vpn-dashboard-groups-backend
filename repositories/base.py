"""
Base repository — generic JSON file persistence.

When migrating to a real DB, replace this class's implementation.
Everything above (services, routes) stays unchanged.
"""

import json
from pathlib import Path
from typing import TypeVar, Generic, Callable
import threading

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Thread-safe JSON file repository."""

    def __init__(
        self,
        filepath: str,
        serializer: Callable[[T], dict],
        deserializer: Callable[[dict], T],
    ):
        self._filepath = Path(filepath)
        self._serialize = serializer
        self._deserialize = deserializer
        self._lock = threading.Lock()

    def _read_raw(self) -> list[dict]:
        """Read the JSON file. Returns empty list if file doesn't exist."""
        if not self._filepath.exists():
            return []
        try:
            with open(self._filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _write_raw(self, data: list[dict]) -> None:
        """Write the full list to JSON file."""
        self._filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_all(self) -> list[T]:
        with self._lock:
            return [self._deserialize(d) for d in self._read_raw()]

    def get_by_id(self, item_id: str, id_field: str = "id") -> T | None:
        with self._lock:
            for d in self._read_raw():
                if d.get(id_field) == item_id:
                    return self._deserialize(d)
        return None

    def add(self, item: T) -> T:
        with self._lock:
            data = self._read_raw()
            data.append(self._serialize(item))
            self._write_raw(data)
        return item

    def update(self, item_id: str, item: T, id_field: str = "id") -> T | None:
        with self._lock:
            data = self._read_raw()
            for i, d in enumerate(data):
                if d.get(id_field) == item_id:
                    data[i] = self._serialize(item)
                    self._write_raw(data)
                    return item
        return None

    def delete(self, item_id: str, id_field: str = "id") -> bool:
        with self._lock:
            data = self._read_raw()
            filtered = [d for d in data if d.get(id_field) != item_id]
            if len(filtered) == len(data):
                return False
            self._write_raw(filtered)
            return True

    def replace_all(self, items: list[T]) -> None:
        """Replace the entire dataset (used for matrix toggle, seeding)."""
        with self._lock:
            self._write_raw([self._serialize(item) for item in items])

    def count(self) -> int:
        with self._lock:
            return len(self._read_raw())

    def exists(self) -> bool:
        """Check if the data file exists and has content."""
        return self._filepath.exists() and self._filepath.stat().st_size > 2
