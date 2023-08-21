import json
from math import ceil

import requests

session = requests.Session()


def get_pixnet_articles(id="", params={}):
    resp = session.get(
        f"https://emma.pixnet.cc/blog/articles/{id}",
        params={"user": "mickey1124", "format": "json", **params},
    )
    resp.raise_for_status()
    return resp.json()


PER_PAGE = 500
page, total_pages = 1, 1
while page <= total_pages:
    data = get_pixnet_articles(
        params={"status": 2, "trim_user": 1, "page": page, "per_page": PER_PAGE}
    )
    articles = data["articles"]
    total_pages = ceil(data["total"] / PER_PAGE)
    print(data["message"], f"Page {page}/{total_pages}")
    page += 1

    # Save the articles to files
    for article in articles:
        last_modified = article["last_modified"]

        # Check if the article has been modified since last download
        filename = f"posts/{article['id']}.json"
        try:
            with open(filename, "r") as f:
                existing_data = json.load(f)
            existing_last_modified = existing_data["last_modified"]
            if last_modified == existing_last_modified:
                continue
        except FileNotFoundError:
            pass
        except json.decoder.JSONDecodeError:
            pass

        article_data = get_pixnet_articles(article["id"])
        assert article_data["message"] == "Show article successfully"
        assert article_data["error"] == 0
        # Save the article to a file
        with open(filename, "w") as f:
            json.dump(article_data["article"], f)

# TODO: delete removed posts
# TODO: assert count
