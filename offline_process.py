import re
from pathlib import Path
from string import Template
from typing import List

from bs4 import BeautifulSoup

posts = Path("docs/_posts")


def update_links():
    links_update = {
        r"https?://mickey1124.pixnet.net/blog/post/": "/posts/",
        r"<div>(/posts/\d+)</div>": r'<a href="\1" target="_blank">\1</a>',
        r'<p><font color="#008080">﹡﹡﹡﹡﹡﹡﹡</font><a href="http://blog.roodo.com/yml/archives/cat_144649.html" target="_blank"><font color="#006699">回應本文前請先按此</font></a><font color="#006699">&nbsp;﹡﹡﹡﹡﹡﹡﹡</font></p>': "",
        # r"https?://mickey1124.pixnet.net/blog/category/list/(\d+)": r"/categories/\1",
        **generate_new_links(),
    }
    for post in posts.iterdir():
        with open(post) as f:
            article = f.read()
            for pattern, repl in links_update.items():
                article = re.sub(pattern, repl, article)
        with open(post, "wt") as f:
            f.write(article)


def generate_new_links():
    articles = [parse_article(post) for post in posts.iterdir()]
    roodo_links = find_roodo_links(articles)

    urls = {}
    for path in posts.iterdir():
        article = parse_article(path)
        urls[article["title"]] = f"/posts/{str(path).split('-')[-1].split('.')[0]}"

    new_links = {}
    for title, link in roodo_links:
        matches = match_articles(articles, title)
        if len(matches) == 1:
            new_links[link] = urls[matches[0]["title"]]
    return new_links


def find_roodo_links(articles):
    roodo_links = []
    for article in articles:
        soup = BeautifulSoup(article["body"])
        roodo_links += [
            (br.previous_sibling, br.next_sibling)
            for br in soup.find_all("br")
            if str(br.next_sibling).startswith("http://blog.roodo")
        ]
        roodo_links += [
            (r.text, r.attrs["href"])
            for r in soup.find_all("a", href=re.compile("roodo"))
        ]
    return roodo_links


def match_articles(articles, title):
    matches = [a for a in articles if title.strip().endswith(a["title"])]
    if len(matches) == 0:
        matches = [a for a in articles if title.strip(" 』").endswith(a["title"])]
    return matches


def tag_articles():
    collection_articles = [
        269197240,
        269196960,
        269196944,
        269196788,
        269196744,
        269196668,
        269196648,
        269196332,
        269196264,
        269196128,
        269196108,
        269196064,
    ]
    tags = {}
    for collection_article in collection_articles:
        with open(find_article(collection_article)) as f:
            tag = f.readlines()[1].split(":")[-1].replace("相關文章", "").strip()

            f.seek(0)
            article = f.read()
            tagged_ids = re.findall(r"/posts/(\d+)", article)

            for id in tagged_ids:
                tags[id] = tags.get(id, set()).union({tag})

    for id, tags in tags.items():
        tag_article(id, list(tags))


def tag_article(article_id, tags: List[str]):
    path = find_article(article_id)
    article_data = parse_article(path)
    article_data["tags"] = tags
    write_article(path, article_data)


def find_article(article_id, mode="rt"):
    return next(posts.glob(f"*-{article_id}.md"))


def parse_article(path):
    with open(path) as f:
        lines = f.readlines()
        return {
            "title": re.findall(r"title: (.*)", lines[1])[0],
            "last_modified": re.findall(r"last_modified_at: (.*)", lines[2])[0],
            "category": re.findall(r"category: (.*)", lines[3])[0],
            "tags": re.findall(r"tags: (.*)", lines[4])[0],
            "body": "".join(lines[7:]),
        }


def write_article(path, data):
    with open("post_template.md") as f:
        updated = Template(f.read()).substitute(data)
    with open(path, "w") as f:
        f.write(updated)


if __name__ == "__main__":
    update_links()
    tag_articles()
