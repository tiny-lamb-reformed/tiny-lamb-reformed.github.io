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
    print(data["message"])

    article = data["article"]
    article["body"] = article["body"].replace(
        "https://mickey1124.pixnet.net/blog/post/", "/posts/",
    )
    with open("post_template.md") as f:
        post = Template(f.read()).substitute(article)

    created = datetime.fromtimestamp(int(article["first_published_at"]))
    created += timedelta(hours=8)
    with open(f"docs/_posts/{created.strftime('%Y-%m-%d')}-{article_id}.md", "w") as f:
        f.write(post)


page = 1
total_pages = 1
PER_PAGE = 10
while page <= total_pages:
    data = get_pixnet(
        "articles", {"status": 2, "trim_user": 1, "page": page, "per_page": PER_PAGE}
    )
    total_pages = ceil(data["total"] / PER_PAGE)
    print(data["message"], f"Page {page}/{total_pages}")
    for article in data["articles"]:
        save(article["id"])
    page += 1
