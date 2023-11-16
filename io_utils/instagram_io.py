from result import Ok, Result
from io_utils.abstract_io import AbstractIO, Json


class InstagramIO(AbstractIO):
    def get_history(self) -> Json:
        return {"Nothing": "Yet"}

    def send(self, summary: str) -> Result[str, str]:
        return Ok(summary)
