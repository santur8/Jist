from summarizer.tree_summarizer import TreeSummarizer
from summarizer.identity_summarizer import IdentitySummarizer
from io_utils.dummy_io import DummyIO


def test_simple_json():
    summarized = TreeSummarizer(IdentitySummarizer()).summarize({"layer 0": "user 0: message 0\nuser 1: message 1"})
    expected = "layer 0:\nuser 0: message 0\nuser 1: message 1"
    assert summarized == expected


def test_nested_json():
    summarized = TreeSummarizer(IdentitySummarizer()).summarize({
        "server 0": {
            "channel 0": 
                "user 0: how do you turn this on\n"\
                "user 1: cheese steak jimmy's"
            ,
            "channel 1":
                "user 2: 123\n"\
                "user 3: 456"
        },
        "server 1": {
            "channel 0":
                "user 0: 2\n"\
                "user 1: 3\n"\
                "user 2: 5\n"\
                "user 3: 8"\
        }
    })
    expected = "server 0:\n"\
        "channel 0:\n"\
        "user 0: how do you turn this on\n"\
        "user 1: cheese steak jimmy's\n"\
        "channel 1:\n"\
        "user 2: 123\n"\
        "user 3: 456\n"\
        "server 1:\n"\
        "channel 0:\n"\
        "user 0: 2\n"\
        "user 1: 3\n"\
        "user 2: 5\n"\
        "user 3: 8"
    assert summarized == expected
