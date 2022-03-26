"""Fetch data from source website."""
from datetime import datetime, timedelta, timezone
from math import ceil
from os import remove
from pathlib import Path
from string import Template

import requests


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
            last_modified_source = int(article["last_modified"])
            if last_modified_local != last_modified_source:
                post_content = get_post(article["id"])
                with open(post_name, "w") as f:
                    f.write(post_content)
        page += 1

    assert list(reversed(sorted(fetched_posts))) == fetched_posts
    existing_posts = set(map(str, Path("docs/_posts").iterdir()))
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
    with open("post_template.md") as f:
        return Template(f.read()).substitute(article)


def file_name(article):
    published_epoch = int(article["public_at"])
    tw_timezone = timezone(timedelta(hours=8))
    published = datetime.fromtimestamp(published_epoch, tw_timezone)
    return f"docs/_posts/{published.strftime('%Y-%m-%d')}-{article['id']}.md"


def last_modified(post) -> int:
    try:
        with open(post) as f:
            return int(f.readlines()[2].split(":")[-1])
    except FileNotFoundError as e:
        print(e)
        return -1


if __name__ == "__main__":
    main()
