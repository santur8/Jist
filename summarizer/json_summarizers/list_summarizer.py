from typing import List
from abc import ABC, abstractmethod


class ListSummarizer(ABC):
    @abstractmethod
    def summarize(self, history: List[str]) -> str:
        pass


class JoinListSummarizer(ListSummarizer):
    def summarize(self, history: List[str]) -> str:
        return "\n".join(history)

