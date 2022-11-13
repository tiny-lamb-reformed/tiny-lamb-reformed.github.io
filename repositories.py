import os
from datetime import datetime, timedelta, timezone
from math import ceil
from pathlib import Path
from string import Template
from typing import Dict, Iterable

import requests
import yaml
from algoliasearch.search_client import SearchClient
from bs4 import BeautifulSoup


class Pixnet:
    def __init__(self) -> None:
        self.session = requests.session()
        self.posts: Dict[int, dict] = {}

        PER_PAGE = 500
        page, total_pages = 1, 1
        while page <= total_pages:
            data = self.get_pixnet(
                "articles",
                {"status": 2, "trim_user": 1, "page": page, "per_page": PER_PAGE},
            )
            total_pages = ceil(data["total"] / PER_PAGE)
            print(data["message"], f"Page {page}/{total_pages}")
            for article in data["articles"]:
                article["id"] = int(article["id"])
                article["last_modified"] = int(article["last_modified"])
                article["public_at"] = int(article["public_at"])
                self.posts[article["id"]] = article
            page += 1

    def get_post_body(self, id) -> dict:
        data = self.get_pixnet(f"articles/{id}")
        print(data["message"], id)
        return data["article"]["body"]

    def get_pixnet(self, resource, params={}):
        resp = self.session.get(
            f"https://emma.pixnet.cc/blog/{resource}",
            params={"user": "mickey1124", "format": "json", **params},
        )
        resp.raise_for_status()
        return resp.json()


class Jekyll:
    def __init__(self, path=Path("docs/_posts")) -> None:
        self.path = path
        self.posts: Dict[int, dict] = {}
        for post_path in path.iterdir():
            post = Jekyll.parse_post(post_path)
            self.posts[post["id"]] = post

    def find_post(self, title, threshold=0.35) -> dict:
        def similarly(x, y):
            exclude = set(" ?（轉貼）")
            a = set(x) - exclude
            b = set(y) - exclude
            c = a.intersection(b)
            return float(len(c)) / (len(a) + len(b) - len(c))

        top_match = max(
            self.posts.values(), key=lambda post: similarly(post["title"], title)
        )
        return top_match if similarly(top_match["title"], title) > threshold else None

    def find_post_path(self, id):
        return next(self.path.glob(f"*-{id}.md"))

    def replace_post(
        self,
        id: int,
        title,
        last_modified,
        category,
        tags,
        sidebar,
        body,
        published: int = None,
    ):
        with open("post_template.md") as temp:
            data = Template(temp.read()).substitute(
                {
                    "title": title,
                    "last_modified": last_modified,
                    "category": category,
                    "tags": tags,
                    "sidebar": sidebar or "",
                    "body": body,
                }
            )

        if published:
            tw_timezone = timezone(timedelta(hours=8))
            published_date = datetime.fromtimestamp(published, tw_timezone).strftime(
                "%Y-%m-%d"
            )
            filepath = self.path / f"{published_date}-{id}.md"
        else:
            filepath = self.find_post_path(id)

        with open(filepath, "w") as post:
            post.write(data)

    def delete_post(self, id):
        filepath = self.find_post_path(id)
        os.remove(filepath)

    @staticmethod
    def parse_post(path: Path):
        with open(path) as f:
            front_matter = next(yaml.safe_load_all(f))
            f.seek(0)
            lines = f.readlines()
            content = next(i for i, line in enumerate(lines[1:]) if line == "---\n") + 3
        return {
            "path": path,
            "id": int(path.name.split("-")[-1].split(".")[0]),
            **front_matter,
            "last_modified": front_matter["last_modified_at"],
            "body": "".join(lines[content:]),
        }


class Algolia:
    def __init__(self, api_key: str) -> None:
        self.client = SearchClient.create("8QSPV5R7NU", api_key)
        self.index = self.client.init_index("posts")

    def replace_all(self, posts: Iterable[dict]):
        self.index.replace_all_objects(
            [
                Algolia._create_post_object(post["id"], post["title"], post["body"])
                for post in posts
                if post["category"] != "複習"
            ]
        )

    def posts_count(self) -> int:
        return self.client.list_indices()["items"][0]["entries"]

    def replace_post(self, id: int, title, content):
        self.index.save_object(Algolia._create_post_object(id, title, content))

    def delete_post(self, id: int):
        self.index.delete_object(id)

    @staticmethod
    def _create_post_object(id: int, title, content):
        return {
            "objectID": id,
            "url": f"/posts/{id}",
            "title": title,
            "content": BeautifulSoup(content, features="lxml").get_text(),
        }
