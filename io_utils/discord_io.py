from typing import Optional, Dict, List, Tuple
from discord.abc import PrivateChannel
from result import Result, Ok, Err
from io_utils.abstract_io import AbstractIO
import discord
from discord import CategoryChannel, ForumChannel
from pprint import pformat


class DiscordIO(AbstractIO):
    intents = discord.Intents.default()
    intents.message_content = True

    def __init__(
        self,
        token: str,
        history_limit=100,
        src_channel_name: Optional[str] = None,
        send_to: Optional[int] = None,
    ) -> None:
        self.history_limit = history_limit
        self.send_to = send_to
        self.token = token
        self.src_channel_name = src_channel_name

    def get_history(self) -> str:
        # https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.Context.history
        bot = discord.Client(intents=self.intents)

        history: Dict[str, Dict[str, List[Tuple[str, str]]]] = {}

        @bot.event
        async def on_ready():
            for guild in bot.guilds:
                for channel in guild.text_channels:
                    if self.src_channel_name is not None and channel.name != self.src_channel_name:
                        # if source channel defined, ignore all others
                        continue
                    history.setdefault(guild.name, dict())[channel.name] = [
                        (message.author.name, message.content) async for message in channel.history(limit=self.history_limit)
                    ]
                    history[guild.name][channel.name].reverse()  # the history is fetched in reverse order, thus reverse back to make it normal
            await bot.close()

        bot.run(self.token)
        return history
        #return f"```\n{pformat(history)}\n```" # return hist dict instead of formatting as str

    def send(self, summary: str) -> Result[discord.Message, str]:
        res = Err("Failed to even enter the match closure")
        match self.send_to:
            case None:
                return Err("No target channel was provided")
            case val:
                bot = discord.Client(intents=self.intents)
                @bot.event
                async def on_ready():
                    nonlocal res
                    async def wrapper():
                        channel = bot.get_channel(val)
                        match channel:
                            case ForumChannel() | PrivateChannel() | CategoryChannel():
                                return Err(f"Cannot send message in {channel.__class__}")
                            case None:
                                return Err("The provided channel id is invalid")
                            case _:
                                return Ok(await channel.send(summary))
                    res = await wrapper()
                    await bot.close()
                bot.run(self.token)
        return res

