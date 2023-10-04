from summarizer.abstract_summarizer import AbstractSummarizer


class IdentitySummarizer(AbstractSummarizer):
    def summarize(self, history: str) -> str:
        return history

