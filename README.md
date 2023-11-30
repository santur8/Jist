# Jist

A summarizer framework with supports of several platforms and different summarizers, aims to help users understand the recent news of their personal subscription of information sources such as discord, twitter, reddit, etc.

## How to run the app

```bash
python main.py -c example_app.json
```

You need to use a json file that specifies the input and output platform, as well as the summarizer to use.

### Structure of app description json files

This is the structure of an app that reads 5 historical messages from Discord for each channel in each server. The fetched message would then be fed into `Identity` summarizer, and the summary would be fed into `Dummy` platform, which simply prints out whatever it receives.

```json
{
  "input_io": {
    "name": "Discord",
    "args": {
      "token": "file:secrets/discord_token",
      "history_limit": 5
    }
  },
  "summarizer": {
    "name": "Identity",
    "args": {}
  },
  "output_io": {
    "name": "Dummy",
    "args": {}
  }
}
```

For a full list of args, please refer to the `__init__` method signature of each io platform / summarizer's definition.

## Todo

<details>

- [x] Make a general purpose `main.py` that takes application descriptions stored in (maybe) toml/json config files, and build applications using them.
  - [ ] Modify TUI to create configs, add store / load config ability
- [x] Introduce testing framework.
  - [ ] Add test for app builder
- [x] Add logging support for the whole program.
- [ ] Build more intelligent tokenizers
- [ ] Add more platforms
  - [ ] Slack
  - [x] Telegram
  - [x] Composite inputs & outputs (may require heavy refactor)
- [ ] Add more summarizers
  - [x] [GPT](https://platform.openai.com/docs/api-reference/chat) summarizer
  - [ ] [LangChain](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/language/use-cases/document-summarization/summarization_large_documents_langchain.ipynb) summarizer
  - [ ] Local inference
    - [x] [finetuned Flan-T5 Base](https://huggingface.co/philschmid/flan-t5-base-samsum)
      - [x] Call model
      - [x] Optimize inference result (maybe introduce formatter?)

</details>
