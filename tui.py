import json
from typing import List, Tuple

from textual.app import App, ComposeResult
from textual.containers import Center, Horizontal, VerticalScroll, Container
from textual.widgets import (
    Button,
    Label,
    ProgressBar,
    RadioSet,
    RadioButton,
    RichLog,
    Rule,
    TextArea,
)

from factories import IOFactory, SummarizerFactory, AppFactory

from app import App as SummaryApp
import nest_asyncio

from io_utils.dummy_io import DummyIO

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
        self.platforms = list(IOFactory.MAP.keys())
        self.summarizers = list(SummarizerFactory.MAP.keys())
        self.platform_i = 0
        self.summarizer_i = 0

    def compose(self) -> ComposeResult:
        with Horizontal():
            with VerticalScroll():
                with Horizontal():
                    with VerticalScroll():
                        with RadioSet(name="Platforms"):
                            yield Label("Platform")
                            for i, name in enumerate(self.platforms):
                                yield RadioButton(name, value=i == self.platform_i)
                        # store platform-specifc settings
                        yield Container(name="Settings", id="input_platform_settings")
                    with VerticalScroll():
                        with RadioSet(name="Summarizers"):
                            yield Label("Summarizer")
                            for i, name in enumerate(self.summarizers):
                                yield RadioButton(name, value=i == self.summarizer_i)
                        yield Container(name="Settings", id="summarizer_settings")
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
            app = AppFactory.new(
                {
                    "input_io": platform_io,
                    "summarizer": summarizer,
                    "output_io": "Dummy",
                }
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
