"""Fetch data from source website."""
from repositories import Jekyll, Pixnet


def main():
    jekyll = Jekyll()
    pixnet = Pixnet()

    for id, live_post in pixnet.posts.items():
        saved_post = jekyll.posts.get(id)
        if not saved_post or saved_post["last_modified"] != live_post["last_modified"]:
            jekyll.update_post(
                live_post["id"],
                live_post["title"],
                live_post["last_modified"],
                live_post["category"],
                [],
                None,
                pixnet.get_post_body(id),
                live_post["public_at"],
            )

    deleted_post_ids = jekyll.posts.keys() - pixnet.posts.keys()
    for id in deleted_post_ids:
        jekyll.delete_post(id)


if __name__ == "__main__":
    main()
