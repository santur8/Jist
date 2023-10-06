from io_utils.discord_io import DiscordIO
from io_utils.dummy_io import DummyIO
from summarizer.identity_summarizer import IdentitySummarizer
from app import App


with open("discord_token", "r") as f:
    token = f.read()

def main():
    dummy_app = App(DiscordIO(token, history_limit=3), IdentitySummarizer(), DummyIO())
    print(dummy_app.summarize())

if __name__ == "__main__":
    main()
