from abc import ABC, abstractmethod
from typing import Dict, Any


Json = Dict[str, Any]


class JsonSummarizer(ABC):
    @abstractmethod
    def summarize(self, history: Json) -> str:
        pass
