from typing import Iterable
from .str_summarizer import StrSummarizer
from transformers import pipeline


class FlanT5BaseSamsumSummarizer(StrSummarizer):
    def __init__(self, block_size: int = 500, hop_size: int = 400) -> None:
        self.pipe = pipeline("text2text-generation", model="philschmid/flan-t5-base-samsum")
        self.block_size = block_size;
        self.hop_size = hop_size;

    def tokenize(self, history: str) -> Iterable[str]:
        for i in range(0, len(history), self.hop_size):
            yield history[i: i + self.block_size]

    def summarize(self, history: str) -> str:
        return "\n".join(self.pipe(token)[0]["generated_text"] for token in self.tokenize(history))

