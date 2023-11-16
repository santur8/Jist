from abstract_summarizer import AbstractSummarizer
from typing import Awaitable, Dict, Any
import asyncio
from functools import partial


Json = Dict[str, Any]


class TreeSummarizer:
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
        return self.summarizer.summarize("\n".join(f"{k}:\n{v}" for k, v in subtree_sum.items()))


class AsyncTreeSummarizer:
    """
    Do the same job as `TreeSummarizer`, except that this class exploits the independency between tree nodes at the same depth
    """

    def __init__(self, summarizer: AbstractSummarizer) -> None:
        self.summarizer = summarizer

    async def _async_summarize(self, s: str) -> Awaitable[str]:
        return asyncio.to_thread(partial(self.summarizer.summarize, s))


    async def summarize(self, history: Json) -> str:
        subtree_sum: Dict[str, asyncio.Task] = {}
        for k, v in history.items():
            match v:
                case dict():
                    subtree_sum[k] = asyncio.create_task(self.summarize(v))
                case str():
                    subtree_sum[k] = asyncio.create_task(self._async_summarize(v))

        await asyncio.gather(*subtree_sum.values())

        return self.summarizer.summarize("\n".join(f"{k}:\n{v.result()}" for k, v in subtree_sum.items()))

