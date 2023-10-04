from io_utils.dummy_io import DummyIO
from summarizer.identity_summarizer import IdentitySummarizer
from app import App

dummy_app = App(DummyIO(), IdentitySummarizer())
print(dummy_app.summarize())
