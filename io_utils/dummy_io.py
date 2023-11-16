from result import Ok, Result
from io_utils.abstract_io import AbstractIO, Json


class DummyIO(AbstractIO):
    def get_history(self) -> Json:
        return {"Dummy": "Dummy"}

    def send(self, summary: str) -> Result[str, str]:
        return Ok(summary)
