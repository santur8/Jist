from io_utils.discord_io import DiscordIO
from io_utils.dummy_io import DummyIO
from summarizer.gpt_MR_summarizer import GPTMRSummarizer
import json

from app import App


with open("./secrets/discord_token", "r") as f:
    token = f.read()

with open("./secrets/channel_id", "r") as f:
    channel_id = int(f.read())

with open("./secrets/openai_api_key", "r") as f:
    api_key = f.read().strip()

tg_secrets = json.load(open("./secrets/tg_secrets.json", "r"))

def main():
    discord_app = App(
        DiscordIO(token, history_limit=20, src_channel_name='general'),
        GPTMRSummarizer(api_key, 4),
        DummyIO()
    )
    print(discord_app.execute())


if __name__ == "__main__":
    main()
