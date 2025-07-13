# utils.py

import re
from config import DISCOURSE_BASE_URL
import os
import requests
from urllib.parse import urlparse, unquote, urljoin

def get_clean_filename(url: str) -> str:
    """
    Extracts a clean filename from a URL by removing query parameters like ?dl=1
    """
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    return unquote(filename)

def extract_upload_links_from_html(html: str) -> list[str]:
    """
    Extracts all links to PDFs/images from the post HTML, including external links.
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a['href']
        if any(href.lower().endswith(ext) for ext in [".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg"]):
            links.append(href)

    return links

def extract_pdf_links_from_text(html: str) -> list[str]:
    return re.findall(r'https?://[^\s]+\.pdf', html)

def download_file(url: str, save_dir: str = "downloads"):
    os.makedirs(save_dir, exist_ok=True)
    filename = get_clean_filename(url)
    file_path = os.path.join(save_dir, filename)

    try:
        with requests.get(url, stream=True, timeout=10) as r:
            r.raise_for_status()
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"✅ Downloaded: {filename}")
    except Exception as e:
        print(f"⚠️ Failed to download {url}: {e}")
