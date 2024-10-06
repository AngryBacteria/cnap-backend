from threading import Lock
from typing import Any


class Singleton:
    _instance: Any = None
    _lock: Lock = Lock()

    def __new__(cls) -> Any:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance


# Usage
singleton1 = Singleton()
singleton2 = Singleton()

print(singleton1 is singleton2)  # True
