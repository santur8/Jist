from io_utils.discord_io import DiscordIO
from io_utils.dummy_io import DummyIO
from summarizer.identity_summarizer import IdentitySummarizer
from app import App


with open("discord_token", "r") as f:
    token = f.read()

with open("channel_id", "r") as f:
    channel_id = int(f.read())

def main():
    discord_app = App(
        DiscordIO(token, history_limit=2),
        IdentitySummarizer(),
        # DummyIO()
        DiscordIO(token, send_to=channel_id),
    )
    print(discord_app.execute())


if __name__ == "__main__":
    main()
