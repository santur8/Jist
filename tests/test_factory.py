from factories import SummarizerFactory
from summarizer.json_summarizers.tree_summarizer import TreeSummarizer
from summarizer.str_summarizers.identity_summarizer import IdentitySummarizer


def test_summarizer_factory_identity():
    summarizer = SummarizerFactory.new("Identity")
    assert isinstance(summarizer, TreeSummarizer)
    assert isinstance(summarizer.str_summarizer, IdentitySummarizer)
