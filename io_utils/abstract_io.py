from typing import TypeVar, Dict, Any
from result import Result
from abc import ABC, abstractmethod


T = TypeVar("T")
Json = Dict[str, Any]


class AbstractIO(ABC):
    @abstractmethod
    def get_history(self) -> Json:
        pass

    @abstractmethod
    def send(self, summary: str) -> Result[T, str]:
        pass
