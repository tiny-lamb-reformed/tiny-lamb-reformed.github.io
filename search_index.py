import json
from bs4 import BeautifulSoup

from offline_process import articles

index = [
    {
        "title": article["title"],
        "content": BeautifulSoup(article["body"], features="lxml").get_text(),
    }
    for article in articles
    if article["category"] != "複習"
]

with open("index.json", "w") as f:
    json.dump(index, f)
