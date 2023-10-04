from abc import ABC, abstractmethod

class AbstractSummarizer(ABC):
    @abstractmethod
    def summarize(self, history: str) -> str:
        pass

