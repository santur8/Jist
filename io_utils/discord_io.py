from typing import Optional
from result import Result, Ok, Err
from io_utils.abstract_io import AbstractIO
import discord
from discord import TextChannel
import asyncio


class DiscordIO(AbstractIO):
    def __init__(
        self,
        client: discord.Client,
        token: str,
        history_limit=100,
        send_to: Optional[TextChannel] = None,
    ) -> None:
        print("Init discord IO ...", end="", flush=True)
        self.client = client
        self.history_limit = history_limit
        self.send_to = send_to
        asyncio.run(self.client.login(token))
        print(" done")

    def __del__(self):
        asyncio.run(self.client.close())

    def get_history(self) -> str:
        # https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.Context.history
        # TODO: also include guild information
        async def get_guilds():
            return [guild async for guild in self.client.fetch_guilds(limit=150)]
        guilds = asyncio.run(get_guilds())
        print(guilds)
        async def get_messages() -> str:
            messages = [
                message
                async for guild in self.client.fetch_guilds(limit=150)
                for channel in guild.channels if isinstance(channel, discord.TextChannel)
                async for message in channel.history(limit=self.history_limit)
            ]
            return str(messages)
        return asyncio.run(get_messages())

    def send(self, summary: str) -> Result[discord.Message, str]:
        if self.send_to is not None:
            return Ok(asyncio.run(self.send_to.send(summary)))
        return Err("No target channel was provided")
