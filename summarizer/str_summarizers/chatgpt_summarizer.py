from .str_summarizer import StrSummarizer
from openai import OpenAI
from loguru import logger


class ChatGPTSummarizer(StrSummarizer):
    def __init__(self, api_key: str) -> None:
        self.client = OpenAI(api_key=api_key)
        logger.info("initialized openai client")

    def summarize(self, history: str) -> str:
        logger.info("start completion")
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that summarizes chat historys to help user grasp recent news in an online chat room."},
                {"role": "user", "content": str(history)}
            ]
        )
        logger.info("completion done")
        assert completion.choices[0].message.content is not None
        return completion.choices[0].message.content

