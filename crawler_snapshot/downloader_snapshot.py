# main.py

import requests
import json
import time
from pathlib import Path

SNAPSHOT_API = "https://hub.snapshot.org/graphql"
SPACE = "opcollective.eth"

OUTPUT_DIR = Path("./data/")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROPOSALS_PATH = OUTPUT_DIR / "proposals.jsonl"
VOTES_PATH = OUTPUT_DIR / "votes.jsonl"

def fetch_proposals(limit=1000):
    query = f"""
    query {{
      proposals(
        first: {limit},
        where: {{ space_in: ["{SPACE}"] }},
        orderBy: "created",
        orderDirection: desc
      ) {{
        id
        title
        body
        author
        start
        end
        created
        choices
        type
        plugins
        strategies {{
          name
          params
        }}
        space {{
          id
          name
        }}
      }}
    }}
    """
    resp = requests.post(SNAPSHOT_API, json={"query": query})
    resp.raise_for_status()
    return resp.json()["data"]["proposals"]

def fetch_all_votes(proposal_id, overlap_seconds=10):
    all_votes = {}
    page_size = 1000
    last_timestamp = int(time.time())

    # alternatively: Use the Snapshot Subgraph (The Graph), more robust and faster (?)
    while True:
        query = """
        query Votes($proposal: String!, $first: Int!, $created_lt: Int!) {
          votes(
            first: $first
            where: { proposal: $proposal, created_lt: $created_lt }
            orderBy: "created"
            orderDirection: desc
          ) {
            id
            voter
            choice
            vp
            created
          }
        }
        """
        variables = {
            "proposal": proposal_id,
            "first": page_size,
            "created_lt": last_timestamp,
        }

        resp = requests.post(SNAPSHOT_API, json={"query": query, "variables": variables})
        resp.raise_for_status() # TODO: need retry logic
        data = resp.json()
        page_votes = data["data"]["votes"]

        if not page_votes:
            break

        for v in page_votes:
            all_votes[v["id"]] = v  # deduping by unique vote id

        # Set new upper bound (overlapping window to avoid missing ties)
        min_created = min(v["created"] for v in page_votes)
        last_timestamp = min_created + 1 - overlap_seconds

        if last_timestamp <= 0:
            break

        time.sleep(0.2)  # Be polite to API

    return list(all_votes.values())

def save_jsonl(filename, items):
    with open(filename, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")

def append_jsonl(filename, items):
    with open(filename, "a", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")

def main():
    print("📥 Fetching proposals...")
    proposals = fetch_proposals(limit=1000)
    save_jsonl(PROPOSALS_PATH, proposals)
    print(f"✅ Saved {len(proposals)} proposals to {PROPOSALS_PATH}")

    print("📥 Fetching votes for each proposal...")
    all_votes = []
    for i, proposal in enumerate(proposals):
        proposal_id = proposal["id"]
        title = proposal["title"][:60].replace("\n", " ")
        print(f"  [{i+1}/{len(proposals)}] → {proposal_id} — {title}...")

        try:
            votes = fetch_all_votes(proposal_id=proposal_id)
            for vote in votes:
                vote["proposal_id"] = proposal_id
            all_votes.extend(votes)
            time.sleep(0.5)
        except Exception as e:
            print(f"    ❌ Failed to fetch votes for {proposal_id}: {e}")

    save_jsonl(VOTES_PATH, all_votes)
    print(f"✅ Saved {len(all_votes)} votes to {VOTES_PATH}")
    print("🏁 Done.")

if __name__ == "__main__":
    main()
