import json
from typing import Callable, List, Any, Dict, Literal, TypeVar

from app import App
from io_utils.abstract_io import AbstractIO
from summarizer.json_summarizers.json_summarizer import JsonSummarizer, Json


def lazy_build_discord_io(**kwargs) -> AbstractIO:
    from io_utils.discord_io import DiscordIO
    return DiscordIO(**kwargs)


def lazy_build_telegram_io(**kwargs) -> AbstractIO:
    from io_utils.telegram_io import TelegramIO

    return TelegramIO(**kwargs)


def lazy_build_text_file_io(**kwargs) -> AbstractIO:
    from io_utils.text_file_io import TextFileIO

    return TextFileIO(**kwargs)


def lazy_build_dummy_io(**kwargs) -> AbstractIO:
    from io_utils.dummy_io import DummyIO

    return DummyIO()


class IOFactory:
    IOKeys = Literal["Discord", "Telegram", "Text File", "Dummy"]

    MAP: Dict[IOKeys, Callable[..., AbstractIO]] = {
        "Discord": lazy_build_discord_io,
        "Telegram": lazy_build_telegram_io,
        "Text File": lazy_build_text_file_io,
        "Dummy": lazy_build_dummy_io,
    }

    @classmethod
    def new(cls, io: IOKeys, **kwargs) -> AbstractIO:
        if io in cls.MAP:
            return cls.MAP[io](**kwargs)
        raise ValueError(
            "%s is not supported. Please use one of the following io: %s"
            % (io, ", ".join(cls.MAP.keys()))
        )


def lazy_build_chatgpt_recursive(**kwargs) -> JsonSummarizer:
    from summarizer.json_summarizers.tree_summarizer import TreeSummarizer
    from summarizer.str_summarizers.chatgpt_summarizer import ChatGPTSummarizer

    return TreeSummarizer(ChatGPTSummarizer(**kwargs))


def lazy_build_chatgpt_mapreduce(**kwargs) -> JsonSummarizer:
    from summarizer.json_summarizers.gpt_MR_summarizer import GPTMRSummarizer

    return GPTMRSummarizer(**kwargs)


def lazy_build_identity(**kwargs) -> JsonSummarizer:
    from summarizer.json_summarizers.tree_summarizer import TreeSummarizer
    from summarizer.str_summarizers.identity_summarizer import IdentitySummarizer

    return TreeSummarizer(IdentitySummarizer())


def lazy_build_flan_t5_base_samsum(**kwargs) -> JsonSummarizer:
    from summarizer.json_summarizers.tree_summarizer import TreeSummarizer
    from summarizer.str_summarizers.flan_t5_base_samsum_summarizer import (
        FlanT5BaseSamsumSummarizer,
    )

    return TreeSummarizer(FlanT5BaseSamsumSummarizer(**kwargs))


class SummarizerFactory:
    SummarizerKeys = Literal[
        "ChatGPT recursive", "ChatGPT MapReduce", "Identity", "Flan T5 base samsum"
    ]

    MAP: Dict[SummarizerKeys, Callable[..., JsonSummarizer]] = {
        "ChatGPT recursive": lazy_build_chatgpt_recursive,
        "ChatGPT MapReduce": lazy_build_chatgpt_mapreduce,
        "Identity": lazy_build_identity,
        "Flan T5 base samsum": lazy_build_flan_t5_base_samsum,
    }

    @classmethod
    def new(
        cls,
        summarizer: SummarizerKeys,
        **kwargs,
    ) -> JsonSummarizer:
        if summarizer in cls.MAP:
            return cls.MAP[summarizer](**kwargs)
        raise ValueError(
            "%s is not supported. Please use one of the following summarizer: %s"
            % (summarizer, ", ".join(cls.MAP.keys()))
        )


T = TypeVar("T", Dict[str, Any], List, str)


class AppFactory:
    """define an app using a json file, builds corresponding application"""

    @classmethod
    def dispatch(cls, obj: T) -> T:
        match obj:
            case dict():
                return {k: cls.dispatch(v) for k, v in obj.items()}
            case list():
                return [cls.dispatch(s) for s in obj]
            case str():
                if obj.startswith("file:"):
                    with open(obj[len("file:") :], "r") as f:
                        return f.read()
                return obj
            case int():
                return obj

    @classmethod
    def replace_secret(cls, obj: Json) -> Json:
        # replace all string starts with `file:` with file content
        return cls.dispatch(obj)

    @classmethod
    def new(cls, config: Json) -> App:
        input_io = cls.replace_secret(config["input_io"])
        summarizer = cls.replace_secret(config["summarizer"])
        output_io = cls.replace_secret(config["output_io"])
        return App(
            IOFactory.new(input_io["name"], **input_io["args"]),
            SummarizerFactory.new(summarizer["name"], **summarizer["args"]),
            IOFactory.new(output_io["name"], **output_io["args"]),
        )
