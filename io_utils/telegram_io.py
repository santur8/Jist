from typing import Optional, Dict, List, Tuple
from result import Result, Ok, Err
from io_utils.abstract_io import AbstractIO
from telethon import TelegramClient
from telethon.sessions.string import StringSession


class TelegramIO(AbstractIO):
    def __init__(self, api_id: int, api_hash: str) -> None:
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = TelegramClient("./secrets/.session", self.api_id, self.api_hash)

    def get_history(self) -> str:
        async def _get_history():
            async for dialog in self.client.iter_dialogs():
                print(dialog.name, dialog.is_group)
        with self.client:
            self.client.loop.run_until_complete(_get_history())
        return ""

    def send(self, summary: str) -> Result[None, str]:
        return Err("TelegramIO.sent() has not been implemented yet")
