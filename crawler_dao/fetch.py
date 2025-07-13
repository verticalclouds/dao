# fetch.py

import requests
import time
from config import DISCOURSE_BASE_URL, REQUEST_HEADERS, SLEEP_BETWEEN_REQUESTS

def get_categories():
    resp = requests.get(f"{DISCOURSE_BASE_URL}/categories.json", headers=REQUEST_HEADERS)
    return resp.json()['category_list']['categories']

def get_category_topics(category_id, max_pages=2):
    topics = []
    for page in range(max_pages):
        url = f"{DISCOURSE_BASE_URL}/c/{category_id}.json?page={page}"
        resp = requests.get(url, headers=REQUEST_HEADERS)
        if resp.status_code != 200:
            break
        data = resp.json()
        page_topics = data.get("topic_list", {}).get("topics", [])
        if not page_topics:
            break
        topics.extend(page_topics)
        time.sleep(SLEEP_BETWEEN_REQUESTS)
    return topics

def get_full_topic_posts(topic_id):
    """
    Returns all posts in the topic (not just the first one),
    including raw and cooked content.
    """
    url = f"{DISCOURSE_BASE_URL}/t/{topic_id}.json"
    resp = requests.get(url, headers=REQUEST_HEADERS)
    if resp.status_code != 200:
        return []

    topic_data = resp.json()
    post_ids = topic_data.get('post_stream', {}).get('stream', [])

    all_posts = []
    for post_id in post_ids:
        post_url = f"{DISCOURSE_BASE_URL}/posts/{post_id}.json"
        post_resp = requests.get(post_url, headers=REQUEST_HEADERS)
        if post_resp.status_code == 200:
            post_data = post_resp.json()
            all_posts.append({
                'id': post_data['id'],
                'post_number': post_data['post_number'],
                'username': post_data['username'],
                'created_at': post_data['created_at'],
                'cooked': post_data['cooked'],  # rendered HTML
                'raw': post_data['raw'],
                'reply_to': post_data.get('reply_to_post_number'),
                'topic_id': topic_id
            })
            print(f"process post id: {post_data['id']}, date: {post_data['created_at']}, user: {post_data['username']}")
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    return all_posts


if False: # version 0
    import requests
    import time
    from config import DISCOURSE_BASE_URL, REQUEST_HEADERS, SLEEP_BETWEEN_REQUESTS

    def get_categories():
        resp = requests.get(f"{DISCOURSE_BASE_URL}/categories.json", headers=REQUEST_HEADERS)
        return resp.json()['category_list']['categories']

    def get_category_topics(category_id, max_pages=2):
        topics = []
        for page in range(max_pages):
            url = f"{DISCOURSE_BASE_URL}/c/{category_id}.json?page={page}"
            resp = requests.get(url, headers=REQUEST_HEADERS)
            if resp.status_code != 200:
                break
            data = resp.json()
            page_topics = data.get("topic_list", {}).get("topics", [])
            if not page_topics:
                break
            topics.extend(page_topics)
            time.sleep(SLEEP_BETWEEN_REQUESTS)
        return topics

    def get_topic(topic_id):
        url = f"{DISCOURSE_BASE_URL}/t/{topic_id}.json"
        resp = requests.get(url, headers=REQUEST_HEADERS)
        if resp.status_code != 200:
            return None
        return resp.json()
