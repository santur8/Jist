# Jist

A summarizer framework with supports of several platforms and different summarizers, aims to help users understand the recent news of their personal subscription of information sources such as discord, twitter, reddit, etc.

## How to run the app

```bash
python main.py
```

## How to change app behavior

Currently you'll have to change the source code in `main.py`, or write your own IO/summarizer/applications.

## Todo

- [ ] Make a general purpose `main.py` that takes application descriptions stored in (maybe) toml/json config files, and build applications using them.
- [ ] Introduce testing framework.
- [ ] Add logging support for the whole program.
- [ ] Add more platforms
  - [ ] (Optional) Investigate the possibility of using discord application and [OAuth2](https://discord.com/developers/docs/topics/oauth2) to read messages instead of bots
  - [ ] Composite inputs & outputs (may require heavy refactor)
- [ ] Add more summarizers
  - [x] [GPT](https://platform.openai.com/docs/api-reference/chat) summarizer
  - [ ] [LangChain](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/language/use-cases/document-summarization/summarization_large_documents_langchain.ipynb) summarizer
  - [ ] Local inference
    - [ ] [finetuned Flan-T5 Base](https://huggingface.co/philschmid/flan-t5-base-samsum)
      - [x] Call model
      - [ ] Optimize inference result (maybe introduce formatter?)

