# main.py

from process import extract_posts
from save import save_jsonl
from utils import extract_upload_links_from_html, download_file, extract_pdf_links_from_text
import json

RAW_PATH = "./data/raw_discourse_posts.jsonl"
OUT_PATH = "./data/optimism_discourse_corpus.jsonl"

def load_jsonl(path):
    with open(path, "r") as f:
        return [json.loads(line) for line in f]

def main():
    raw_posts = load_jsonl(RAW_PATH)

    print(f"🔍 Loaded {len(raw_posts)} raw posts")

    all_docs = extract_posts(raw_posts)
    print(f"📝 Extracted {len(all_docs)} structured docs")

    for post in raw_posts:
        html = post.get("cooked", "")
        upload_links = extract_upload_links_from_html(html)
        upload_links.extend(extract_pdf_links_from_text(html))
        for url in upload_links:
            download_file(url=url, save_dir='./data/downloads')

    save_jsonl(all_docs, OUT_PATH)
    print(f"\n✅ Saved {len(all_docs)} structured posts to {OUT_PATH}")

if __name__ == "__main__":
    main()
