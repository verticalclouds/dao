# downloader_dao.py
import time
import json
from pathlib import Path
from datetime import datetime, timezone

from fetch import get_categories, get_category_topics, get_full_topic_posts
from config import TARGET_CATEGORY_SLUGS, MAX_PAGES_PER_CATEGORY

RAW_DATA_PATH = Path("./data/raw_discourse_posts.jsonl")

def get_target_category_ids():
    categories = get_categories()
    return [
        c["id"]
        for c in categories
        if c["slug"] in TARGET_CATEGORY_SLUGS
    ]

def save_jsonl(documents, out_path):
    with open(out_path, "w") as f:
        for doc in documents:
            f.write(json.dumps(doc) + "\n")

def main():
    all_raw_posts = []
    category_ids = get_target_category_ids()

    for cat_id in category_ids:
        print(f"\n📥 Fetching topics from category ID {cat_id}")
        topics = get_category_topics(cat_id, max_pages=MAX_PAGES_PER_CATEGORY)

        for topic in topics:
            topic_id = topic["id"]
            posts = get_full_topic_posts(topic_id)

            # 💡 MINIMAL ANNOTATION ONLY — keep everything else raw
            for post in posts:
                post["downloaded_at"] = datetime.now(timezone.utc).isoformat()
                post["topic_slug"] = topic.get("slug")
                post["topic_title"] = topic.get("title")
                post["topic_id"] = topic.get("id")

            all_raw_posts.extend(posts)

    save_jsonl(all_raw_posts, RAW_DATA_PATH)
    print(f"\n✅ Saved {len(all_raw_posts)} raw posts to {RAW_DATA_PATH}")

if __name__ == "__main__":
    main()
