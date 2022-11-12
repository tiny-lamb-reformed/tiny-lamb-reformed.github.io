import re
from typing import Iterable, List, Tuple

import yaml
from bs4 import BeautifulSoup

from repositories import Jekyll


def process_all():
    jekyll = Jekyll()

    links_replace: List[tuple] = [
        (r"https?://mickey1124.pixnet.net/blog/post/", "/posts/"),
        (r"<div>(/posts/\d+)</div>", r'<a href="\1" target="_blank">\1</a>'),
        (
            r'<p><font color="#008080">﹡﹡﹡﹡﹡﹡﹡</font><a href="http://blog.roodo.com/yml/archives/cat_144649.html" target="_blank"><font color="#006699">回應本文前請先按此</font></a><font color="#006699">&nbsp;﹡﹡﹡﹡﹡﹡﹡</font></p>',
            "",
        ),
        *[
            (
                f"https://mickey1124.pixnet.net/blog/category/list/{id}",
                f"/categories/#{label}",
            )
            for id, label in [
                (3270876, "護教、福音"),
                ("3270864/1", "預定論與自由意志"),
                (3270864, "預定論與自由意志"),
                (3270848, "信仰與婚姻"),
                (3270852, "聖經無誤、解經原則"),
                (3728449, "禮拜更新"),
            ]
        ],
    ]
    for title, old_link in find_roodo_links(jekyll.posts.values()):
        match = jekyll.find_post(title)
        if "cat_" not in old_link and match:
            links_replace.append((old_link, f"/posts/{match['id']}"))

    with open("docs/_data/navigation.yml") as f:
        all_nav = yaml.safe_load(f)
        series = {
            category: [
                child["url"].strip("/posts")
                for nav in all_nav[category]
                for child in nav["children"]
            ]
            for category in ["predestination", "gospel"]
        }

    for id, post in jekyll.posts.items():
        try:
            if str(id) in series["predestination"]:
                sidebar = "{ title: 預定論精選文章, nav: predestination }"
            elif str(id) in series["gospel"]:
                sidebar = "{ nav: gospel }"
            else:
                sidebar = None
            jekyll.update_post(
                id,
                title=re.sub(
                    r' " (.*) " ', "「\g<1>」", post["title"]
                ),  # TODO: validation may be needed
                last_modified=post["last_modified"],
                category=post["category"],
                tags=[],
                sidebar=sidebar,
                body=update_links(links_replace, post["body"]),
            )
        except Exception as e:
            print(f"Process article failed: {id}")
            raise e


def find_roodo_links(posts) -> Iterable[Tuple[str, str]]:
    for post in posts:
        soup = BeautifulSoup(post["body"], features="lxml")
        for br in soup.find_all("br"):
            if str(br.next_sibling).strip().startswith("http://blog.roodo"):
                yield (br.previous_sibling, br.next_sibling)

        for a in soup.find_all("a", href=re.compile("roodo")):
            yield (a.text, a.attrs["href"])


def update_links(new_links: List[tuple], body: str) -> str:
    for pattern, repl in new_links:
        body = re.sub(pattern, repl, body)

    soup = BeautifulSoup(body, features="lxml")

    # convert xxx<br>/posts/... to <a href="/posts/...">xxx</a>
    soup_updated = False
    for br in soup.find_all("br"):
        if str(br.next_sibling).strip().startswith("/posts/"):
            soup_updated = True
            title = br.previous_sibling
            link = br.next_sibling
            link_tag = soup.new_tag("a", href=str(link))
            link_tag.string = title
            title.replace_with(link_tag)
            link.replace_with("")
            br.decompose()

    return soup.body.decode_contents() if soup_updated else body


if __name__ == "__main__":
    process_all()
