from abc import ABC, ABCMeta, abstractmethod
from asyncio import Server
import json
from typing import List, Tuple, Dict, Optional, Protocol, Union

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Center, Horizontal, Vertical, VerticalScroll, Container
from textual.events import Mount
from textual.validation import Number
from textual.widget import Widget
from textual.widgets import (
    Button,
    Input,
    Label,
    ProgressBar,
    RadioSet,
    RadioButton,
    RichLog,
    Rule,
    Static,
    TextArea,
)

import discord
import nest_asyncio

from app import App as SummaryApp
from factories import IOFactory, SummarizerFactory, AppFactory
from io_utils.abstract_io import Json

nest_asyncio.apply()


with open("./secrets/discord_token", "r") as f:
    token = f.read()

with open("./secrets/channel_id", "r") as f:
    channel_id = int(f.read())

with open("./secrets/openai_api_key", "r") as f:
    api_key = f.read().strip()

tg_secrets = json.load(open("./secrets/tg_secrets.json", "r"))


class BuildConfigWidget(Widget):
    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )

    def build_config(self) -> Json:
        raise NotImplementedError


class DiscordSettings(BuildConfigWidget):
    def __init__(self, token: str) -> None:
        super().__init__()
        self.token = token

        # assume we only support summarizing only one channel...
        self.servers: List[Tuple[str, int]] = []
        self.channels: List[Tuple[str, int]] = []

        self.selected_server_i: Optional[int] = None
        self.selected_channel_i: Optional[int] = None

        self.history_limit = 100

        bot = discord.Client(intents=discord.Intents.default())

        @bot.event
        async def on_ready():
            for guild in bot.guilds:
                self.servers.append((guild.name, guild.id))
            await bot.close()

        bot.run(self.token)

    def on_mount(self) -> None:
        self.build_server_widget()

    def build_server_widget(self):
        widget = self.query_one("#server_list", Container)
        widget.remove_children()
        r = RadioSet(id="server_radio_set")
        r.mount(Label("servers"))
        for k, _ in self.servers:
            r.mount(RadioButton(k))
        widget.mount(r)

    @on(RadioSet.Changed, "#server_radio_set")
    def build_channel_widget(self, event: RadioSet.Changed):
        widget = self.query_one("#channel_list", Container)
        widget.remove_children()

        self.selected_server_i = event.radio_set.pressed_index - 1
        _, guild_id = self.servers[self.selected_server_i]

        self.channels.clear()
        bot = discord.Client(intents=discord.Intents.default())

        @bot.event
        async def on_ready():
            self.channels.clear()
            guild = bot.get_guild(guild_id)
            if guild is not None:
                for channel in guild.text_channels:
                    self.channels.append((channel.name, channel.id))
            await bot.close()

        bot.run(self.token)

        r = RadioSet(id="channel_radio_set")
        r.mount(Label("channels"))
        for k, _ in self.channels:
            r.mount(RadioButton(k))
        widget.mount(r)

    @on(RadioSet.Changed, "#channel_radio_set")
    def update_channel_i(self, event: RadioSet.Changed):
        self.selected_channel_i = event.radio_set.pressed_index - 1

    @on(Input.Changed, "#input")
    def update_history_limit(self, event: Input.Changed):
        self.history_limit = int(event.input.value)

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Container(id="server_list")
            yield Container(id="channel_list")
            yield Input(
                id="input",
                placeholder="history limit (max 100)",
                validators=[
                    Number(minimum=1, maximum=100),
                ],
            )

    def build_config(self) -> Json:
        return {
            "token": self.token,
            "history_limit": self.history_limit,
            "src_channel_name": self.channels[self.selected_channel_i][0]
            if self.selected_channel_i is not None
            else None,
        }


class DummySettings(BuildConfigWidget):
    def __init__(self) -> None:
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Static("dummy")

    def build_config(self) -> Json:
        return {}


class IOSettingsFactory:
    @staticmethod
    def new(io: IOFactory.IOKeys) -> BuildConfigWidget:
        match io:
            case "Discord":
                return DiscordSettings(token)
            case "Telegram":
                raise NotImplementedError()
            case "Text File":
                raise NotImplementedError()
            case "Dummy":
                return DummySettings()
            case _:
                raise ValueError("not supported IO... how could TUI go this wrong?")


class SummarizerTUIApp(App[None]):
    def __init__(self):
        super().__init__()
        self.platforms: List[IOFactory.IOKeys] = list(IOFactory.MAP.keys())
        self.summarizers: List[SummarizerFactory.SummarizerKeys] = list(
            SummarizerFactory.MAP.keys()
        )
        self.platform_i = 0
        self.summarizer_i = 0

        self.platform_config: Optional[BuildConfigWidget] = None

    def compose(self) -> ComposeResult:
        with Horizontal():
            with VerticalScroll():
                with Horizontal():
                    with VerticalScroll():
                        with RadioSet(name="Platforms"):
                            yield Label("Platform")
                            for i, name in enumerate(self.platforms):
                                yield RadioButton(name)
                        # store platform-specifc settings
                        yield Container(id="input_platform_settings")
                    with VerticalScroll():
                        with RadioSet(name="Summarizers"):
                            yield Label("Summarizer")
                            for i, name in enumerate(self.summarizers):
                                yield RadioButton(name)
                        # yield Container(name="Settings", id="summarizer_settings")
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

            platform_io = self.platforms[self.platform_i]
            summarizer = self.summarizers[self.summarizer_i]
            app = AppFactory.new(
                {
                    "input_io": {
                        "name": platform_io,
                        "args": self.platform_config.build_config()
                        if self.platform_config is not None
                        else None,
                    },
                    "summarizer": {"name": summarizer, "args": {}},
                    "output_io": {"name": "Dummy", "args": {}},
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

    def build_platform_settings(self):
        container = self.query_one("#input_platform_settings", Container)
        container.remove_children()
        self.platform_config = IOSettingsFactory.new(self.platforms[self.platform_i])
        container.mount(self.platform_config)

    def on_radio_set_changed(self, event: RadioSet.Changed):
        match event.radio_set.name:
            case "Platforms":
                self.platform_i = event.radio_set.pressed_index - 1
                self.build_platform_settings()
            case "Summarizers":
                self.summarizer_i = event.radio_set.pressed_index - 1


if __name__ == "__main__":
    SummarizerTUIApp().run()
