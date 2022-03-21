import re
from pathlib import Path
from string import Template
from typing import Tuple

from bs4 import BeautifulSoup


def parse_article(path: Path):
    with open(path) as f:
        lines = f.readlines()
        return {
            "id": path.name.split("-")[-1].split(".")[0],
            "title": re.findall(r"title: (.*)", lines[1])[0],
            "last_modified": re.findall(r"last_modified_at: (.*)", lines[2])[0],
            "category": re.findall(r"category: (.*)", lines[3])[0],
            "tags": re.findall(r"tags: (.*)", lines[4])[0],
            "body": "".join(lines[7:]),
        }


posts = Path("docs/_posts")
articles = [parse_article(post) for post in posts.iterdir()]


def process_all():
    new_links = {
        r"https?://mickey1124.pixnet.net/blog/post/": "/posts/",
        r"<div>(/posts/\d+)</div>": r'<a href="\1" target="_blank">\1</a>',
        r'<p><font color="#008080">﹡﹡﹡﹡﹡﹡﹡</font><a href="http://blog.roodo.com/yml/archives/cat_144649.html" target="_blank"><font color="#006699">回應本文前請先按此</font></a><font color="#006699">&nbsp;﹡﹡﹡﹡﹡﹡﹡</font></p>': "",
        # r"https?://mickey1124.pixnet.net/blog/category/list/(\d+)": r"/categories/\1",
        **generate_new_links(),
    }
    tags = generate_tags()
    for post in posts.iterdir():
        article = parse_article(post)
        update_links(new_links, article)
        article["tags"] = list(tags.get(article["id"], []))
        write_article(post, article)

    move_to_collection()


def generate_new_links():
    new_links = {}
    for title, link in find_roodo_links():
        matches = match_articles(articles, title)
        if len(matches) == 1:
            new_links[link] = f"/posts/{matches[0]['id']}"
    return new_links


def find_roodo_links() -> Tuple[str, str]:
    for article in articles:
        soup = BeautifulSoup(article["body"])
        for br in soup.find_all("br"):
            if str(br.next_sibling).startswith("http://blog.roodo"):
                yield (br.previous_sibling, br.next_sibling)

        for a in soup.find_all("a", href=re.compile("roodo")):
            yield (a.text, a.attrs["href"])


def match_articles(articles, title):
    matches = [a for a in articles if title.strip().endswith(a["title"])]
    if len(matches) == 0:
        matches = [a for a in articles if title.strip(" 』").endswith(a["title"])]
    return matches


def generate_tags():
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
    return tags


def update_links(new_links, article):
    for pattern, repl in new_links.items():
        article["body"] = re.sub(pattern, repl, article["body"])

    soup = BeautifulSoup(article["body"])
    for br in soup.find_all("br"):
        if str(br.next_sibling).startswith("/posts/"):
            new_link = soup.new_tag("a", href=str(br.next_sibling))
            new_link.string = br.previous_sibling
            br.previous_sibling.replace_with(new_link)
            br.next_sibling.replace_with("")
            br.decompose()

    article["body"] = soup.body.decode_contents()


def move_to_collection():
    pass


def find_article(article_id, mode="rt"):
    return next(posts.glob(f"*-{article_id}.md"))


def write_article(path, data):
    with open("post_template.md") as f:
        updated = Template(f.read()).substitute(data)
    with open(path, "w") as f:
        f.write(updated)


if __name__ == "__main__":
    process_all()
