from summarizer.abstract_summarizer import AbstractSummarizer
from openai import OpenAI

class ChatGPTSummarizer(AbstractSummarizer):
    def __init__(self, api_key: str) -> None:
        self.client = OpenAI(api_key=api_key)

    def summarize(self, history: str) -> str:
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that summarizes chat historys to help user grasp recent news in an online chat room."},
                {"role": "user", "content": str(history)}
                ]
        )
        assert completion.choices[0].message.content is not None
        return completion.choices[0].message.content

