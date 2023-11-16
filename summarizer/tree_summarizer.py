from abc import ABC, abstractmethod
from .abstract_summarizer import AbstractSummarizer
from typing import Dict, Any
import asyncio
from functools import partial


Json = Dict[str, Any]


class JsonSummarizer(ABC):
    @abstractmethod
    def summarize(self, history: Json) -> str:
        pass


class TreeSummarizer(JsonSummarizer):
    """
    Summarizes nested tree-structured data. Recursively flattens and summarizes subtrees,
    useful for models not trained on tree-structured chat history.
    """

    def __init__(self, summarizer: AbstractSummarizer) -> None:
        self.summarizer = summarizer

    def summarize(self, history: Json) -> str:
        subtree_sum = {}
        for k, v in history.items():
            match v:
                case dict():
                    subtree_sum[k] = self.summarize(v)
                case str():
                    subtree_sum[k] = self.summarizer.summarize(v)
        return self.summarizer.summarize("\n".join("%s:\n%s" % (k, v) for k, v in subtree_sum.items()))


class AsyncTreeSummarizer(JsonSummarizer):
    """
    Do the same job as `TreeSummarizer`, except that this class exploits the independency between tree nodes at the same depth
    """

    def __init__(self, summarizer: AbstractSummarizer) -> None:
        self.summarizer = summarizer

    async def async_summarize(self, history: Json) -> str:
        subtree_sum: Dict[str, asyncio.Task] = {}
        for k, v in history.items():
            match v:
                case dict():
                    subtree_sum[k] = asyncio.create_task(self.async_summarize(v))
                case str():
                    subtree_sum[k] = asyncio.create_task(asyncio.to_thread(partial(self.summarizer.summarize, v)))

        await asyncio.gather(*subtree_sum.values())

        return self.summarizer.summarize("\n".join(f"{k}:\n{v.result()}" for k, v in subtree_sum.items()))

    def summarize(self, history: Json) -> str:
        return asyncio.get_running_loop().run_until_complete(self.async_summarize(history))
