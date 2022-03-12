"""Get all data from source website."""
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
    with open("post_template.md") as f:
        post = Template(f.read()).substitute(data["article"])

    with open(f"docs/_posts/{article_id}.md", "w") as f:
        f.write(post)


data = get_pixnet("articles", {"status": 2, "trim_user": 1})
print(data["message"])
articles = data["articles"]

for article in articles[:10]:
    save(article["id"])
