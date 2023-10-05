from io_utils.discord_io import DiscordIO
from io_utils.dummy_io import DummyIO
from summarizer.identity_summarizer import IdentitySummarizer
from app import App
import discord


intents = discord.Intents.default()
intents.message_content = True
discord_client = discord.Client(intents=intents)

with open("discord_token", "r") as f:
    token = f.read()

def main():
    print("main start")
    dummy_app = App(DiscordIO(discord_client, token), IdentitySummarizer(), DummyIO())
    print(dummy_app.summarize())

if __name__ == "__main__":
    main()
