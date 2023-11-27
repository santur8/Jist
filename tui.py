import json
from typing import List, Tuple

from textual.app import App, ComposeResult
from textual.containers import Center, Horizontal, VerticalScroll
from textual.widgets import Button, Label, ProgressBar, RadioSet, RadioButton, RichLog, Rule, TextArea
from io_utils.abstract_io import AbstractIO
from io_utils.discord_io import DiscordIO
from io_utils.dummy_io import DummyIO
from io_utils.instagram_io import InstagramIO
from io_utils.telegram_io import TelegramIO
from io_utils.text_file_io import TextFileIO
from summarizer.str_summarizers.identity_summarizer import IdentitySummarizer
from summarizer.str_summarizers.chatgpt_summarizer import ChatGPTSummarizer
from summarizer.json_summarizers.tree_summarizer import TreeSummarizer
from summarizer.json_summarizers.gpt_MR_summarizer import GPTMRSummarizer

from app import App as SummaryApp
import nest_asyncio
nest_asyncio.apply()


with open("./secrets/discord_token", "r") as f:
    token = f.read()

with open("./secrets/channel_id", "r") as f:
    channel_id = int(f.read())

with open("./secrets/openai_api_key", "r") as f:
    api_key = f.read().strip()

tg_secrets = json.load(open("./secrets/tg_secrets.json", "r"))


class SummarizerTUIApp(App[None]):
    def __init__(self):
        super().__init__()
        self.platforms: List[Tuple[str, AbstractIO]] = [
            ("Discord", DiscordIO(token, history_limit=30, src_channel_name="simulation")),
            ("Instagram", InstagramIO()),
            ("Telegram", TelegramIO(tg_secrets["api_id"], tg_secrets["api_hash"])),
            ("Text File", TextFileIO("data/discord_history.txt")),
        ]
        self.summarizers = [
            ("ChatGPT recursive", TreeSummarizer(ChatGPTSummarizer(api_key))),
            ("ChatGPT MapReduce", GPTMRSummarizer(api_key, 3, True)),
            ("Identity", TreeSummarizer(IdentitySummarizer())),
            ("Flan T5 base samsum", TreeSummarizer(IdentitySummarizer())),  # for faster loading
        ]
        self.platform_i = 0
        self.summarizer_i = 0

    def compose(self) -> ComposeResult:
        with Horizontal():
            with VerticalScroll():
                with Horizontal():
                    with RadioSet(name="Platforms"):
                        yield Label("Platform")
                        for i, (label, _) in enumerate(self.platforms):
                            yield RadioButton(label, value=i == self.platform_i)
                    with RadioSet(name="Summarizers"):
                        yield Label("Summarizer")
                        for i, (label, _) in enumerate(self.summarizers):
                            yield RadioButton(label, value=i == self.summarizer_i)
            yield Rule("vertical")
            with VerticalScroll():
                area = RichLog(id="summary", wrap=True)
                yield area
                with Center():
                    yield ProgressBar(100, show_eta=False, id="progress_bar")
                with Center():
                    yield Button("summarize", id="summarize")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "summarize":
            event.button.disabled = True
            pb = self.query_one("#progress_bar", ProgressBar)

            _, platform_io = self.platforms[self.platform_i]
            _, summarizer = self.summarizers[self.summarizer_i]
            app = SummaryApp(
                platform_io,
                summarizer,
                DummyIO()
            )

            area = self.query_one("#summary", RichLog)
            area.clear()

            pb.progress = 0
            hist = app.input_io.get_history()
            pb.advance(33)
            sum = app.summarizer.summarize(hist)
            pb.advance(33)
            res = app.output_io.send(sum)
            area.write(res.unwrap_or("something goes wrong"))
            pb.advance(34)
            event.button.disabled = False

    def on_radio_set_changed(self, event: RadioSet.Changed):
        match event.radio_set.name:
            case "Platforms":
                self.platform_i = event.radio_set.pressed_index - 1
            case "Summarizers":
                self.summarizer_i = event.radio_set.pressed_index - 1


if __name__ == "__main__":
    SummarizerTUIApp().run()
