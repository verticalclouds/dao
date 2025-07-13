# process.py

from bs4 import BeautifulSoup

def html_to_text(html):
    return BeautifulSoup(html, "html.parser").get_text()

def extract_posts(posts):
    docs = []
    for post in posts:
        doc = {
            "topic_id": post.get("topic_id"),
            "topic_slug": post.get("topic_slug"),
            "topic_title": post.get("topic_title"),
            "post_number": post.get("post_number"),
            "username": post.get("username"),
            "created_at": post.get("created_at"),
            "raw": post.get("raw"),
        }
        docs.append(doc)
    return docs

if False:
    def extract_posts(topic_json):
        topic_id = topic_json["id"]
        title = topic_json["title"]
        slug = topic_json["slug"]
        posts = topic_json["post_stream"]["posts"]

        doc_chunks = []
        for post in posts:
            doc_chunks.append({
                "topic_id": topic_id,
                "slug": slug,
                "title": title,
                "post_number": post["post_number"],
                "username": post["username"],
                "created_at": post["created_at"],
                "raw_html": post["cooked"],
                "text": html_to_text(post["cooked"]),
            })
        return doc_chunks
