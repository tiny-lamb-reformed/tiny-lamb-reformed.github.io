"""Get all data from source website."""
from datetime import datetime, timedelta
from math import ceil
from string import Template

import requests


def get_pixnet(resource, params={}):
    resp = requests.get(
        f"https://emma.pixnet.cc/blog/{resource}",
        params={"user": "mickey1124", "format": "json", **params},
    )
    resp.raise_for_status()
    return resp.json()


def save(article_id):
    data = get_pixnet(f"articles/{article_id}")
    print(data["message"], article_id)

    article = data["article"]
    with open("post_template.md") as f:
        post = Template(f.read()).substitute(article)

    with open(file_name(article), "w") as f:
        f.write(post)


def file_name(article):
    published_epoch = int(article.get("first_published_at") or article["public_at"])
    published = datetime.fromtimestamp(published_epoch) + timedelta(hours=8)
    return f"docs/_posts/{published.strftime('%Y-%m-%d')}-{article['id']}.md"


def modified(article):
    try:
        with open(file_name(article)) as f:
            file_modified = int(f.readlines()[2].split(":")[-1])
        return int(article["last_modified"]) != file_modified
    except FileNotFoundError:
        return True


page = 1
total_pages = 1
PER_PAGE = 200
while page <= total_pages:
    data = get_pixnet(
        "articles", {"status": 2, "trim_user": 1, "page": page, "per_page": PER_PAGE}
    )
    total_pages = ceil(data["total"] / PER_PAGE)
    print(data["message"], f"Page {page}/{total_pages}")
    for article in data["articles"]:
        if modified(article):
            save(article["id"])
    page += 1
