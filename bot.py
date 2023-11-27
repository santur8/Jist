import discord
from discord.ext import commands
from summarizer.json_summarizers.tree_summarizer import TreeSummarizer
from summarizer.json_summarizers.list_summarizer import ListSummarizer, JoinListSummarizer, ChunkListSummarizer
from summarizer.str_summarizers.flan_t5_base_samsum_summarizer import FlanT5BaseSamsumSummarizer
from summarizer.str_summarizers.chatgpt_summarizer import ChatGPTSummarizer
from typing import Any
from loguru import logger


with open("./secrets/openai_api_key", "r") as f:
    api_key = f.read().strip()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", description="Summarizer", intents=intents)
summarizer = TreeSummarizer(ChatGPTSummarizer(api_key))
# list_summarizer = ChunkListSummarizer(FlanT5BaseSamsumSummarizer(), 400)


# class JistBot(discord.Client):
#     def __init__(self, list_summarizer: ListSummarizer, intents: discord.Intents, **options: Any) -> None:
#         super().__init__(intents=intents, **options)
#         self.list_summarizer = list_summarizer

#     async def on_ready(self):
#         print(f"Logged on as {self.user}!")

#     async def on_message(self, message: discord.Message):
#         if message.content == "summarize":
#             await message.channel.send("supposed `to` *be* **some** ~~summarized~~ text")
#             # msg_history = [
#             #     "%s: %s" % (message.author.name, message.content) async for message in message.channel.history(limit=50)
#             # ]
#             # msg_history.reverse()
#             # await message.channel.send(self.list_summarizer.summarize(msg_history))


@bot.command()
async def summarize(ctx: commands.Context):
    logger.info("received command")
    msg_history = [
        "%s: %s" % (message.author.name, message.content) async for message in ctx.channel.history(limit=50)
    ]
    msg_history.reverse()
    guild = ctx.guild
    guild_name = guild.name if guild is not None else ""
    await ctx.channel.send(summarizer.summarize({guild_name: msg_history}))

with open("./secrets/discord_token", "r") as f:
    token = f.read()

bot.run(token)
# client = JistBot(ChunkListSummarizer(FlanT5BaseSamsumSummarizer(), 400), intents=intents)
# client.run(token)
