# Writeup Collector

The Writeup Collector is a tool for sending new medium's write-ups to the discord channel

## Installation

So simple.

1. Add your [medium RSS feeds](https://help.medium.com/hc/en-us/articles/214874118-Using-RSS-feeds-of-profiles-publications-and-topics) to [feed.txt](./feeds.txt).
2. Replace your config in the [config.py](./config.py) file.
3. run these commands.

```sh
pip install -r requirements.txt
python3 main.py
```

| If you want to run it, such as scheduled tasks. customize the [jobs.py](./jobs.py) file and execute it.
