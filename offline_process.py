import re
from pathlib import Path
from string import Template
from typing import Tuple

import yaml
from bs4 import BeautifulSoup


def parse_article(path: Path):
    with open(path) as f:
        front_matter = next(yaml.safe_load_all(f))
        f.seek(0)
        lines = f.readlines()
        content = next(i for i, line in enumerate(lines[1:]) if line == "---\n") + 3
    return {
        "path": path,
        "id": path.name.split("-")[-1].split(".")[0],
        **front_matter,
        "last_modified": front_matter["last_modified_at"],
        "body": "".join(lines[content:]),
    }


posts = Path("docs/_posts")
articles = [parse_article(post) for post in posts.iterdir()]


def process_all():
    new_links = {
        r"https?://mickey1124.pixnet.net/blog/post/": "/posts/",
        r"<div>(/posts/\d+)</div>": r'<a href="\1" target="_blank">\1</a>',
        r'<p><font color="#008080">﹡﹡﹡﹡﹡﹡﹡</font><a href="http://blog.roodo.com/yml/archives/cat_144649.html" target="_blank"><font color="#006699">回應本文前請先按此</font></a><font color="#006699">&nbsp;﹡﹡﹡﹡﹡﹡﹡</font></p>': "",
        **generate_new_category_links(),
        **generate_new_links(),
    }

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

    for article in articles:
        try:
            article["title"] = re.sub(
                r' " (.*) " ', "「\g<1>」", article["title"]
            )  # TODO: validation may be needed
            update_links(new_links, article)
            if article["id"] in series["predestination"]:
                article["sidebar"] = "{ title: 預定論精選文章, nav: predestination }"
            elif article["id"] in series["gospel"]:
                article["sidebar"] = "{ nav: gospel }"
            write_article(article)
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


def generate_new_category_links():
    categories = {
        3270876: "護教、福音",
        "3270864/1": "預定論與自由意志",
        3270864: "預定論與自由意志",
        3270848: "信仰與婚姻",
        3270852: "聖經無誤、解經原則",
        3728449: "禮拜更新",
    }
    return {
        f"https://mickey1124.pixnet.net/blog/category/list/{id}": f"/categories/#{label}"
        for id, label in categories.items()
    }


def generate_new_links():
    new_links = {}
    for title, link in find_roodo_links():
        if "cat_" not in link:
            match = search_article(title)
            if title_similarly(match["title"], title) > 0.35:
                new_links[link] = f"/posts/{match['id']}"
    return new_links


def find_roodo_links() -> Tuple[str, str]:
    for article in articles:
        soup = BeautifulSoup(article["body"], features="lxml")
        for br in soup.find_all("br"):
            if str(br.next_sibling).strip().startswith("http://blog.roodo"):
                yield (br.previous_sibling, br.next_sibling)

        for a in soup.find_all("a", href=re.compile("roodo")):
            yield (a.text, a.attrs["href"])


def search_article(title):
    return max(articles, key=lambda a: title_similarly(a["title"], title))


def title_similarly(x, y):
    exclude = set(" ?（轉貼）")
    a = set(x) - exclude
    b = set(y) - exclude
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))


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
        if str(br.next_sibling).strip().startswith("/posts/"):
            new_link = soup.new_tag("a", href=str(br.next_sibling))
            new_link.string = br.previous_sibling
            br.previous_sibling.replace_with(new_link)
            br.next_sibling.replace_with("")
            br.decompose()

    article["body"] = soup.body.decode_contents()


def find_article(article_id, mode="rt"):
    return next(posts.glob(f"*-{article_id}.md"))


def write_article(data: dict):
    if data.get("sidebar") is None:
        data["sidebar"] = ""
    with open("post_template.md") as f:
        updated = Template(f.read()).substitute(data)
    with open(data["path"], "w") as f:
        f.write(updated)


if __name__ == "__main__":
    process_all()
