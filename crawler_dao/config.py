# config.py

# Base URL for the Discourse forum
DISCOURSE_BASE_URL = "https://gov.optimism.io/"

# Slugs of Discourse categories you want to crawl
TARGET_CATEGORY_SLUGS = [
    'get-started',
    'gov-fund-missions',
    'delegates',
    'retrofunding',
    'citizens',
    'elected-reps',
    'technical-proposals',
    'policies-and-important-documents',
    'collective-strategy',
    'updates-and-announcements',
    'gov-design',
    'feedback',
    'accountability',
    'general'
]

# Headers for polite crawling
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:138.0) Gecko/20100101 Firefox/138.0"
}

# Crawling options
MAX_PAGES_PER_CATEGORY = 3
SLEEP_BETWEEN_REQUESTS = 0.3  # seconds
