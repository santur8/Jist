from result import Ok, Result
from io_utils.abstract_io import AbstractIO


class DummyIO(AbstractIO):
    def get_history(self) -> str:
        return "Dummy"

    def send(self, summary: str) -> Result[str, str]:
        return Ok(summary)
