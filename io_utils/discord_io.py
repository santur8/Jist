from typing import Optional, Dict, List, Tuple
from result import Result, Ok, Err
from io_utils.abstract_io import AbstractIO
import discord
from discord import TextChannel
import asyncio


class DiscordIO(AbstractIO):
    def __init__(
        self,
        token: str,
        history_limit=100,
        send_to: Optional[TextChannel] = None,
    ) -> None:
        self.history_limit = history_limit
        self.send_to = send_to
        self.token = token

    def get_history(self) -> str:
        # https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.Context.history
        # TODO: also include guild information
        intents = discord.Intents.default()
        intents.message_content = True
        bot = discord.Client(intents=intents)

        history: Dict[str, Dict[str, List[Tuple[str, str]]]] = {}

        @bot.event
        async def on_ready():
            for guild in bot.guilds:
                for channel in guild.text_channels:
                    history.setdefault(guild.name, dict())[channel.name] = [
                        (message.author.name, message.content) async for message in channel.history(limit=self.history_limit)
                    ]
            await bot.close()

        bot.run(self.token)
        return str(history)

    def send(self, summary: str) -> Result[discord.Message, str]:
        if self.send_to is not None:
            return Ok(asyncio.run(self.send_to.send(summary)))
        return Err("No target channel was provided")
