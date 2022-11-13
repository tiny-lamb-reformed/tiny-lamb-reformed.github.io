"""Fetch data from Pixnet and synchronize data in Jekyll and Algolia search index."""
import sys

from repositories import Algolia, Jekyll, Pixnet


def main(algolia_api_key):
    jekyll = Jekyll()
    algolia = Algolia(algolia_api_key)
    pixnet = Pixnet()

    for id, live_post in pixnet.posts.items():
        saved_post = jekyll.posts.get(id)
        if not saved_post or saved_post["last_modified"] != live_post["last_modified"]:
            body = pixnet.get_post_body(id)
            jekyll.replace_post(
                live_post["id"],
                live_post["title"],
                live_post["last_modified"],
                live_post["category"],
                [],
                None,
                body,
                live_post["public_at"],
            )
            if live_post["category"] != "複習":
                algolia.replace_post(id, live_post["title"], body)

    deleted_post_ids = jekyll.posts.keys() - pixnet.posts.keys()
    for id in deleted_post_ids:
        jekyll.delete_post(id)
        algolia.delete_post(id)

    assert len(pixnet.posts) == len(jekyll.posts)
    assert (
        sum(post["category"] != "複習" for post in jekyll.posts.values())
        == algolia.posts_count()
    )


if __name__ == "__main__":
    algolia_api_key = sys.argv[1]
    main(algolia_api_key)
