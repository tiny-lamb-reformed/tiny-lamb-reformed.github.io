import json
import os
from pathlib import Path

import opencc
from algoliasearch.search_client import SearchClient
from bs4 import BeautifulSoup

# Initialize Algolia client
client = SearchClient.create("8QSPV5R7NU", os.environ["ALGOLIA_API_KEY"])
index = client.init_index("posts-tw")

# t2s.json is the configuration file for Traditional to Simplified conversion
converter = opencc.OpenCC("t2s")

posts = []
for json_file in Path("pipeline/posts").glob("*.json"):
    with open(json_file) as file:
        post = json.load(file)
        if post.get("category") != "複習":
            posts.append(post)

for post in posts:
    body_text = BeautifulSoup(post["body"], features="lxml").get_text()[:16000]
    record = {
        "objectID": post["id"],
        "title": post["title"],
        "title_cn": converter.convert(post["title"]),
        "content": body_text,
        "content_cn": converter.convert(body_text),
    }

    # Update Algolia index with the filtered data
    index.save_object(record).wait()
    print(f"Saved {post['id']} in Algolia index.")

# TODO: delete
assert len(posts) == client.list_indices()["items"][-1]["entries"]
