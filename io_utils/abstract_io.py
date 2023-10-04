from typing import TypeVar
from result import Result
from abc import ABC, abstractmethod

T = TypeVar("T")


class AbstractIO(ABC):
    @abstractmethod
    def get_history(self) -> str:
        pass

    @abstractmethod
    def send(self, summary: str) -> Result[T, str]:
        pass

