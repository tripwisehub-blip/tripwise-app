import os, json
A = "https://tripwisehub-blip.github.io/tripwise-app/"
BOT = "https://t.me/tripwise_hub_bot"
L = {}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "blog_guides.json"), encoding="utf-8") as f:
    GUIDES = json.load(f)
