from typing import TypeVar
from result import Result
from io_utils.abstract_io import AbstractIO
from summarizer.abstract_summarizer import AbstractSummarizer


T = TypeVar("T")


class App:
    def __init__(self, io: AbstractIO, summarizer: AbstractSummarizer) -> None:
        self.io = io
        self.summarizer = summarizer

    def summarize(self) -> Result[T, str]:
        # TODO: should I use inheritance here?
        return self.io.send(self.summarizer.summarize(self.io.get_history()))

