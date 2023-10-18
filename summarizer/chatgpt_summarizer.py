from summarizer.abstract_summarizer import AbstractSummarizer
import openai


class ChatGPTSummarizer(AbstractSummarizer):
    def __init__(self, api_key: str) -> None:
        openai.api_key = api_key

    def summarize(self, history: str) -> str:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that summarizes chat historys to help user grasp recent news in an online chat room."},
                {"role": "user", "content": history}
            ]
        )
        return completion.choices[0].message.content

