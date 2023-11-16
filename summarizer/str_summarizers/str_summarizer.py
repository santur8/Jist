from abc import ABC, abstractmethod


class StrSummarizer(ABC):
    @abstractmethod
    def summarize(self, history: str) -> str:
        pass

