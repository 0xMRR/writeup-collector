# Writeup Collector

The Writeup Collector is a tool for sending new medium's write-ups to the discord channel

## Installation

- Add your [medium RSS feeds](https://help.medium.com/hc/en-us/articles/214874118-Using-RSS-feeds-of-profiles-publications-and-topics) to [feeds.txt](https://github.com/verfosec/writeup-collector/blob/main/feeds.txt).
- put your discord webhook url in [.env](https://github.com/verfosec/writeup-collector/blob/main/.env.sample) file.

```sh
pip install -r requirements.txt
python3 main.py
```

> If you want to run it, such as scheduled tasks. customize the [jobs.py](https://github.com/verfosec/writeup-collector/blob/main/jobs.py) file and execute it.
