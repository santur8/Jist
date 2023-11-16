from .str_summarizer import StrSummarizer


class IdentitySummarizer(StrSummarizer):
    def summarize(self, history: str) -> str:
        return history

