from pathlib import Path
import re

links_update = {
    r"https?://mickey1124.pixnet.net/blog/post/": "/posts/",
    #r"<div>(/posts/\d+)</div>": r'<a href="\1" target="_blank">\1</a>',
    #r"https?://mickey1124.pixnet.net/blog/category/list/(\d+)": r"/categories/\1",
}

posts = Path("docs/_posts")

for post in posts.iterdir():
    with open(post) as f:
        article = f.read()
        for pattern, repl in links_update.items():
            article = re.sub(pattern, repl, article)
    with open(post, "wt") as f:
        f.write(article)
