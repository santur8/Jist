from io_utils.discord_io import DiscordIO
from io_utils.dummy_io import DummyIO
from summarizer.identity_summarizer import IdentitySummarizer
from summarizer.chatgpt_summarizer import ChatGPTSummarizer
from app import App


with open("discord_token", "r") as f:
    token = f.read()

with open("channel_id", "r") as f:
    channel_id = int(f.read())

with open("openai_api_key", "r") as f:
    api_key = f.read().strip()

def main():
    discord_app = App(
        DiscordIO(token, history_limit=10),
        # IdentitySummarizer(),
        ChatGPTSummarizer(api_key),
        DummyIO()
        # DiscordIO(token, send_to=channel_id),
    )
    print(discord_app.execute())


if __name__ == "__main__":
    main()
