import json
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Tuple

import pytz
from bs4 import BeautifulSoup


def create_markdown():
    links_replace: List[tuple] = [
        (r"https?://mickey1124.pixnet.net/blog/post/", "/post/"),
        (r"<div>(/post/\d+)</div>", r'<a href="\1" target="_blank">\1</a>'),
        (
            r'<p><font color="#008080">﹡﹡﹡﹡﹡﹡﹡</font><a href="http://blog.roodo.com/yml/archives/cat_144649.html" target="_blank"><font color="#006699">回應本文前請先按此</font></a><font color="#006699">&nbsp;﹡﹡﹡﹡﹡﹡﹡</font></p>',
            "",
        ),
        *[
            (
                rf"https:\/\/mickey1124\.pixnet\.net\/blog\/category\/(?:list\/)?{id}",
                f"/categories/#{label}",
            )
            for id, label in [
                (3270884, "設立宗旨與管理說明"),
                (3270876, "護教、福音"),
                ("3270864/1", "預定論與自由意志"),
                (3270864, "預定論與自由意志"),
                (3270848, "信仰與婚姻"),
                (3270852, "聖經無誤、解經原則"),
                (3728449, "禮拜更新"),
            ]
        ],
    ]
    posts = read_posts()
    output_dir = Path("../content/zh_TW/post")

    links_replace += [(fix[0], fix[1]) for fix in roodo_links_fix(posts)]

    # Loop through all the JSON files in the input directory
    for post in posts:
        # Format the metadata as a Hugo front matter string
        title = post["title"].replace('"', '\\"')
        date = datetime.fromtimestamp(
            int(post["public_at"]), pytz.timezone("Asia/Taipei")
        ).strftime("%Y-%m-%d")
        lastmod = datetime.fromtimestamp(
            int(post["last_modified"]), pytz.timezone("Asia/Taipei")
        ).strftime("%Y-%m-%d")
        site_migration_date = "2019-01-20"
        if lastmod == site_migration_date:
            lastmod = date
        front_matter = (
            f"+++\n"
            f'title = "{title}"\n'
            f"date = {date}\n"
            f"lastmod = {lastmod}\n"
            f'categories = ["{post["category"]}"]\n'
            f'series = "{clean_title_and_extract_series(title)}"\n'
            f"isCJKLanguage = true\n"
            f"+++\n\n"
        )

        # Combine the front matter, 'rawhtml' shortcode, and content into a single string
        markdown = (
            front_matter
            + "{{< rawhtml >}}\n"
            + update_links(links_replace, post["body"])
            + "\n{{< /rawhtml >}}\n"
        )

        # Write the markdown to a file in the output directory
        output_filename = post["id"] + ".md"
        output_filepath = output_dir / output_filename
        with open(output_filepath, "w") as f:
            f.write(markdown)


def read_posts():
    posts = []
    for filepath in Path("posts").glob("*.json"):
        # Load the JSON data from the file
        with open(filepath, "r") as f:
            posts.append(json.load(f))
    return posts


# define a function to clean up the title column and extract the first substring
def clean_title_and_extract_series(title):
    if title.startswith("發問："):
        title = title[3:]
    return re.split("[：（]", title, maxsplit=1)[0]


def roodo_links_fix(posts):
    fix = []
    for title, old_link in find_roodo_links(posts):
        match = find_post(title, posts)
        if "cat_" not in old_link and match:
            fix.append((old_link, f"/post/{match['id']}", title, match["title"]))
    return fix


def find_roodo_links(posts) -> Iterable[Tuple[str, str]]:
    for post in posts:
        soup = BeautifulSoup(post["body"], features="lxml")
        for br in soup.find_all("br"):
            if str(br.next_sibling).strip().startswith("http://blog.roodo"):
                yield (br.previous_sibling, br.next_sibling)

        for a in soup.find_all("a", href=re.compile("roodo")):
            yield (a.text, a.attrs["href"])


def find_post(title, posts, threshold=0.35) -> dict:
    def similarly(x, y):
        exclude = set(" ?（轉貼）")
        a = set(x) - exclude
        b = set(y) - exclude
        c = a.intersection(b)
        return float(len(c)) / (len(a) + len(b) - len(c))

    top_match = max(posts, key=lambda post: similarly(post["title"], title))
    return top_match if similarly(top_match["title"], title) > threshold else None


def update_links(new_links: List[tuple], body: str) -> str:
    for pattern, repl in new_links:
        body = re.sub(pattern, repl, body)

    soup = BeautifulSoup(body, features="lxml")

    # convert xxx<br>/post/... to <a href="/post/...">xxx</a>
    soup_updated = False
    for br in soup.find_all("br"):
        if str(br.next_sibling).strip().startswith("/post/"):
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
    create_markdown()
