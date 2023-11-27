from typing import List, Iterable
from abc import ABC, abstractmethod

from transformers.pipelines.automatic_speech_recognition import chunk_iter

from summarizer.str_summarizers.str_summarizer import StrSummarizer


class ListSummarizer(ABC):
    @abstractmethod
    def summarize(self, history: List[str]) -> str:
        pass


class JoinListSummarizer(ListSummarizer):
    def summarize(self, history: List[str]) -> str:
        return "\n".join(history)


class ChunkListSummarizer(ListSummarizer):
    def __init__(self, str_summarizer: StrSummarizer, block_size: int) -> None:
        self.str_summarizer = str_summarizer
        self.block_size = block_size

    def chunk_iter(self, history: List[str]) -> Iterable[str]:
        buffer = []
        accu_len = 0
        for msg in history:
            if accu_len + len(msg) + max(len(buffer) - 1, 0) > self.block_size:
                yield "\n".join(buffer)
                buffer.clear()
                accu_len = 0
            buffer.append(msg)
            accu_len += len(msg)
        if buffer:
            yield "\n".join(buffer)
            buffer.clear()
    
    def summarize(self, history: List[str]) -> str:
        return "\n".join(self.str_summarizer.summarize(chunk) for chunk in self.chunk_iter(history))
        # first_pass = [self.str_summarizer.summarize(chunk) for chunk in self.chunk_iter(history)]
        # second_pass = "\n".join(self.str_summarizer.summarize(chunk) for chunk in self.chunk_iter(first_pass))
        # return second_pass
