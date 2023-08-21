import json
import os
import subprocess
from pathlib import Path
from typing import Literal

import opencc
from algoliasearch.search_client import SearchClient
from bs4 import BeautifulSoup


def main():
    # Initialize Algolia client
    client = SearchClient.create("8QSPV5R7NU", os.environ["ALGOLIA_API_KEY"])
    index = client.init_index("posts-bilang")

    # t2s.json is the configuration file for Traditional to Simplified conversion
    converter = opencc.OpenCC("t2s")

    for post in get_posts("deleted"):
        index.delete_object(post["id"]).wait()
        print(f"Deleted {post['id']} in Algolia index.")

    for post in get_posts("changed"):
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

    assert len(get_posts()) == client.list_indices()["items"][-1]["entries"]


def get_posts(mode: Literal["all", "changed", "deleted"] = "all"):
    if mode == "all":
        post_paths = Path("posts").glob("*.json")
    else:
        post_paths = get_changed_files(mode == "deleted")

    posts = []
    for json_file in post_paths:
        with open(json_file) as file:
            post = json.load(file)
            if post.get("category") != "複習":
                posts.append(post)
    return posts


def get_changed_files(deleted):
    # Run the `git` command to get the changed files in the staging area
    cmd = ["git", "ls-files", "posts"] + (
        ["--deleted"] if deleted else ["--modified", "--others"]
    )
    output = subprocess.check_output(cmd, universal_newlines=True)

    # Split the output into a list of file paths
    return output.strip().split("\n") if output else []


if __name__ == "__main__":
    main()
