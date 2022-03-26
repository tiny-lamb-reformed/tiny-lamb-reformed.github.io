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
    for post in posts.iterdir():
        try:
            article = parse_article(post)
            article["title"] = re.sub(r' " (.*) " ', "「\g<1>」", article["title"])
            update_links(new_links, article)
            write_article(post, article)
        except Exception as e:
            print(f"Process article failed: {article}")
            raise e

    title = {a["id"]: a["title"] for a in articles}
    nav = {}
    for group, ids in group_articles():
        nav[group] = {
            "title": group,
            "children": [
                {"title": title[id], "url": f"/posts/{id}#{group}"} for id in ids
            ],
        }
    js = f"var nav_collections = {nav};"
    with open("docs/assets/js/nav_collections.js", "wt") as f:
        f.write(js)


def generate_new_links():
    new_links = {}
    for title, link in find_roodo_links():
        matches = match_articles(articles, title)
        if len(matches) == 1:
            new_links[link] = f"/posts/{matches[0]['id']}"
    return new_links


def find_roodo_links() -> Tuple[str, str]:
    for article in articles:
        soup = BeautifulSoup(article["body"], features="lxml")
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


def group_articles():
    theme_articles = [
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
    for id in theme_articles:
        article = parse_article(find_article(id))
        tag = article["title"].replace("相關文章", "").strip()
        ids = sorted(set(re.findall(r"/posts/(\d+)", article["body"])))
        yield tag, ids


def update_links(new_links, article):
    for pattern, repl in new_links.items():
        article["body"] = re.sub(pattern, repl, article["body"])

    soup = BeautifulSoup(article["body"], features="lxml")
    for br in soup.find_all("br"):
        if str(br.next_sibling).startswith("/posts/"):
            new_link = soup.new_tag("a", href=str(br.next_sibling))
            new_link.string = br.previous_sibling
            br.previous_sibling.replace_with(new_link)
            br.next_sibling.replace_with("")
            br.decompose()

    article["body"] = soup.body.decode_contents()


def find_article(article_id, mode="rt"):
    return next(posts.glob(f"*-{article_id}.md"))


def write_article(path, data):
    with open("post_template.md") as f:
        updated = Template(f.read()).substitute(data)
    with open(path, "w") as f:
        f.write(updated)


if __name__ == "__main__":
    process_all()
