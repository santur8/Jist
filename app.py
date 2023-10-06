from typing import TypeVar
from result import Result
from io_utils.abstract_io import AbstractIO
from summarizer.abstract_summarizer import AbstractSummarizer


T = TypeVar("T")


class App:
    def __init__(
        self,
        input_io: AbstractIO,
        summarizer: AbstractSummarizer,
        output_io: AbstractIO,
    ) -> None:
        self.input_io = input_io
        self.output_io = output_io
        self.summarizer = summarizer

    def execute(self) -> Result[T, str]:
        return self.output_io.send(
            self.summarizer.summarize(self.input_io.get_history())
        )
