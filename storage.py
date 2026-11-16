from typing import Dict, List
from models import AnimalOut, Status
import time

class LogEntry:
    def __init__(self, method: str, path: str, status: int, duration_ms: float):
        self.timestamp = time.time()  # Время в формате Unix Timestamp
        self.method = method
        self.path = path
        self.status = status
        self.duration_ms = duration_ms


class InMemoryStorage:
    def __init__(self):
        self._items: Dict[int, AnimalOut] = {}
        self._next_id: int = 1
        self._logs: List[LogEntry] = []

    def get_next_id(self) -> int:
        current_id = self._next_id
        self._next_id += 1
        return current_id

    def get(self, item_id: int) -> AnimalOut | None:
        return self._items.get(item_id)

    def save(self, item_id: int, item: AnimalOut):
        self._items[item_id] = item

    def delete(self, item_id: int):
        if item_id in self._items:
            del self._items[item_id]

    def values(self):
        return self._items.values()

    def add_log(self, method: str, path: str, status: int, duration_ms: float):
        entry = LogEntry(method, path, status, duration_ms)
        self._logs.append(entry)

    def get_logs(self, limit: int = 100, offset: int = 0):
        total = len(self._logs)
        paginated = self._logs[-(offset + limit):-offset if offset else None][::-1]
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": paginated
        }

_storage_instance: InMemoryStorage | None = None

def _create_animal(storage: InMemoryStorage, name: str, species: str, age: int, status: Status):
    animal_id = storage.get_next_id()
    item = AnimalOut(
        id=animal_id,
        name=name,
        species=species,
        age=age,
        status=status
    )
    storage.save(animal_id, item)


def get_storage() -> InMemoryStorage:
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = InMemoryStorage()

        # --- НАЧАЛО ПРЕДЗАПОЛНЕНИЯ ---
        # 1
        _create_animal(_storage_instance, "Барон", "Собака", 3, Status.IN_SHELTER)
        # 2
        _create_animal(_storage_instance, "Мурка", "Кошка", 1, Status.IN_SHELTER)
        # 3
        _create_animal(_storage_instance, "Рыжик", "Хомяк", 2, Status.IN_SHELTER)
        # # 4
        _create_animal(_storage_instance, "Кеша", "Попугай", 5, Status.IN_SHELTER)
        # # 5
        _create_animal(_storage_instance, "Бусинка", "Кошка", 4, Status.IN_SHELTER)
        # # 6
        _create_animal(_storage_instance, "Шарик", "Собака", 7, Status.IN_SHELTER)
        # # 7
        _create_animal(_storage_instance, "Тоша", "Кролик", 1, Status.IN_SHELTER)
        # # 8
        _create_animal(_storage_instance, "Лаки", "Собака", 2, Status.ADOPTED)
        # # 9
        _create_animal(_storage_instance, "Соня", "Кошка", 3, Status.IN_SHELTER)
        # # 10
        _create_animal(_storage_instance, "Арчи", "Собака", 6, Status.IN_SHELTER)
        # --- КОНЕЦ ПРЕДЗАПОЛНЕНИЯ ---

    return _storage_instance