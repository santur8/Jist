from summarizer.str_summarizers.str_summarizer import StrSummarizer
from .json_summarizer import Json, JsonSummarizer
from .list_summarizer import ListSummarizer, JoinListSummarizer
from typing import Dict
import asyncio
from functools import partial
import json


class TreeSummarizer(JsonSummarizer):
    """
    Summarizes nested tree-structured data. Recursively flattens and summarizes subtrees,
    useful for models not trained on tree-structured chat history.
    """

    def __init__(self, str_summarizer: StrSummarizer, list_summarizer: ListSummarizer = JoinListSummarizer()) -> None:
        self.str_summarizer = str_summarizer
        self.list_summarizer = list_summarizer

    def summarize(self, history: Json) -> str:
        subtree_sum = {}
        for k, v in history.items():
            match v:
                case dict():
                    subtree_sum[k] = self.summarize(v)
                case list():
                    subtree_sum[k] = self.list_summarizer.summarize(v)
                case str():
                    subtree_sum[k] = self.str_summarizer.summarize(v)
        return self.str_summarizer.summarize("\n".join("%s:\n%s" % (k, v) for k, v in subtree_sum.items()))


class IdentityTreeSummarizer(JsonSummarizer):
    def summarize(self, history: Json) -> str:
        return json.dumps(history)


class AsyncTreeSummarizer(JsonSummarizer):
    """
    Do the same job as `TreeSummarizer`, except that this class exploits the independency between tree nodes at the same depth
    """

    def __init__(self, str_summarizer: StrSummarizer, list_summarizer: ListSummarizer = JoinListSummarizer()) -> None:
        self.str_summarizer = str_summarizer
        self.list_summarizer = list_summarizer

    async def async_summarize(self, history: Json) -> str:
        subtree_sum: Dict[str, asyncio.Task] = {}
        for k, v in history.items():
            match v:
                case dict():
                    subtree_sum[k] = asyncio.create_task(self.async_summarize(v))
                case list():
                    subtree_sum[k] = asyncio.create_task(asyncio.to_thread(partial(self.list_summarizer.summarize, v)))
                case str():
                    subtree_sum[k] = asyncio.create_task(asyncio.to_thread(partial(self.str_summarizer.summarize, v)))

        await asyncio.gather(*subtree_sum.values())

        return self.str_summarizer.summarize("\n".join(f"{k}:\n{v.result()}" for k, v in subtree_sum.items()))

    def summarize(self, history: Json) -> str:
        return asyncio.get_running_loop().run_until_complete(self.async_summarize(history))
