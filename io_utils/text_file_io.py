from result import Ok, Result, Err
from io_utils.abstract_io import AbstractIO


class TextFileIO(AbstractIO):
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def get_history(self) -> str:
        with open(self.filename, "r") as f:
            return f.read()

    def send(self, summary: str) -> Result[int, str]:
        try:
            with open(self.filename, "w") as f:
                return Ok(f.write(summary))
        except Exception as e:
            return Err(str(e))
