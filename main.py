# from io_utils.discord_io import DiscordIO
from io_utils.dummy_io import DummyIO
# from io_utils.text_file_io import TextFileIO
from io_utils.telegram_io import TelegramIO
from summarizer.identity_summarizer import IdentitySummarizer
# from summarizer.chatgpt_summarizer import ChatGPTSummarizer
# from summarizer.flan_t5_base_samsum_summarizer import FlanT5BaseSamsumSummarizer
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
        # DiscordIO(token, history_limit=10),
        # TextFileIO("data/discord_history.txt"),
        TelegramIO(tg_secrets["api_id"], tg_secrets["api_hash"]),
        IdentitySummarizer(),
        # ChatGPTSummarizer(api_key),
        # FlanT5BaseSamsumSummarizer(),
        DummyIO()
        # DiscordIO(token, send_to=channel_id),
    )
    print(discord_app.execute())


if __name__ == "__main__":
    main()
