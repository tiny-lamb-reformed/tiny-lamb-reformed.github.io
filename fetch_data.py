"""Fetch data from source website."""
from math import ceil
from os import remove
from pathlib import Path

import requests

from offline_process import write_article


def main():
    page, total_pages = 1, 1
    PER_PAGE = 200
    fetched_posts = []
    while page <= total_pages:
        data = get_pixnet(
            "articles",
            {"status": 2, "trim_user": 1, "page": page, "per_page": PER_PAGE},
        )
        total_pages = ceil(data["total"] / PER_PAGE)
        print(data["message"], f"Page {page}/{total_pages}")
        for article in data["articles"]:
            post_name = file_name(article)
            fetched_posts.append(post_name)
            last_modified_local = last_modified(post_name)
            last_modified_source = int(article["last_modified"]) * 1000
            if last_modified_local != last_modified_source:
                article_data = get_post(article["id"])
                article_data["path"] = post_name
                write_article(article_data)
        page += 1

    existing_posts = set(map(str, Path("source/_posts").iterdir()))
    deleted_posts = existing_posts - set(fetched_posts)
    for deleted_post in deleted_posts:
        remove(deleted_post)


def get_pixnet(resource, params={}):
    resp = requests.get(
        f"https://emma.pixnet.cc/blog/{resource}",
        params={"user": "mickey1124", "format": "json", **params},
    )
    resp.raise_for_status()
    return resp.json()


def get_post(article_id):
    data = get_pixnet(f"articles/{article_id}")
    print(data["message"], article_id)
    article = data["article"]
    article["public_at"] = int(article["public_at"]) * 1000
    article["last_modified"] = int(article["last_modified"]) * 1000
    article["tags"] = []  # pixnet tags may contain JSON
    return article


def file_name(article):
    return f"source/_posts/{article['id']}.md"


def last_modified(post) -> int:
    try:
        with open(post) as f:
            return int(f.readlines()[3].split(":")[-1])
    except FileNotFoundError as e:
        print(e)
        return -1


if __name__ == "__main__":
    main()
