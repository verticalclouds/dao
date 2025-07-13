import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import defaultdict, Counter

def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def save_jsonl(path, items):
    with open(path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")

def parse_iso(dt_str):
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))

def index_votes_by_proposal(votes):
    by_pid = defaultdict(list)
    for v in votes:
        by_pid[v["proposal_id"]].append(v)
    return by_pid

def format_utc(ts):
    if ts is None:
        return None
    return datetime.utcfromtimestamp(ts).replace(tzinfo=timezone.utc).isoformat()

def link_discourse_and_votes(proposals, discourse_posts, votes_by_pid, day_window=3):
    linked = []

    for proposal in proposals:
        prop_time = datetime.utcfromtimestamp(proposal["created"]).replace(tzinfo=timezone.utc)
        min_time = prop_time - timedelta(days=day_window)
        max_time = prop_time + timedelta(days=day_window)

        # Match Discourse posts
        matching_posts = [
            post for post in discourse_posts
            if "created_at" in post and min_time <= parse_iso(post["created_at"]) <= max_time
        ]

        votes = votes_by_pid.get(proposal["id"], [])
        vote_dist = defaultdict(float)
        voter_counter = Counter()
        very_low_vp_threshold = 0.01

        for vote in votes:
            voter_counter[vote["voter"]] += 1
            raw_choice = vote.get("choice")

            if isinstance(raw_choice, int):
                idx = raw_choice - 1
                choices = proposal.get("choices", [])
                label = choices[idx] if 0 <= idx < len(choices) else "Unknown"
                vote_dist[label] += vote.get("vp", 0)

            elif isinstance(raw_choice, list):
                flat_choices = []
                for c in raw_choice:
                    flat_choices.extend(c if isinstance(c, list) else [c])
                choices = proposal.get("choices", [])

                for idx in flat_choices:
                    try:
                        i = int(idx) - 1
                        label = choices[i] if 0 <= i < len(choices) else "Unknown"
                        vote_dist[label] += vote.get("vp", 0)
                    except (ValueError, TypeError):
                        continue  # skip malformed choice

            elif isinstance(raw_choice, dict):
                choices = proposal.get("choices", [])
                for idx_str, weight in raw_choice.items():
                    i = int(idx_str) - 1
                    label = choices[i] if 0 <= i < len(choices) else "Unknown"
                    vote_dist[label] += weight * vote.get("vp", 0)

        total_voters = len(votes)
        total_vp = sum(v.get("vp", 0) for v in votes)
        winning_choice = max(vote_dist.items(), key=lambda x: x[1])[0] if vote_dist else None
        turnout_percent = round((total_vp / 10_000_000) * 100, 2) if total_vp else 0.0

        # Stats
        unique_voters = len(voter_counter)
        voters_with_multiple_votes = [v for v, c in voter_counter.items() if c > 1]
        voters_with_very_low_vp = [v for v in votes if v.get("vp", 0) < very_low_vp_threshold]

        # Determine Discourse URL from any matching post with topic_id and topic_slug
        discourse_url = None
        for post in matching_posts:
            if "topic_id" in post and "topic_slug" in post and "post_number" in post:
                discourse_url = f"https://gov.optimism.io/t/{post['topic_slug']}/{post['topic_id']}/{post['post_number']}"
                break

        joined = {
            "proposal_id": proposal["id"],
            "title": proposal.get("title"),
            "discourse_url": discourse_url,
            "created": proposal.get("created"),
            "snapshot_author": proposal.get("author"),
            "choices": proposal.get("choices", []),
            "space": proposal.get("space", {}),
            "voting": {
                "type": proposal.get("type"),
                "strategies": proposal.get("strategies", []),
                "start_utc": format_utc(proposal.get("start")),
                "end_utc": format_utc(proposal.get("end")),
                "choices": proposal.get("choices", []),
                "result": {
                    "winning_choice": winning_choice,
                    "total_voters": total_voters,
                    "total_voting_power": round(total_vp, 2),
                    "turnout_percent": turnout_percent,
                    "vote_distribution": {k: round(v, 2) for k, v in vote_dist.items()},
                },
                "voter_stats": {
                    "unique_voters": unique_voters,
                    "voters_with_multiple_votes": len(voters_with_multiple_votes),
                    "low_vp_votes": len(voters_with_very_low_vp),
                },
            },
            "engagement": {
                "discourse_post_count": len(matching_posts),
                "unique_posters": len(set(p["username"] for p in matching_posts if "username" in p)),
                "discussion_start": min((p["created_at"] for p in matching_posts), default=None),
                "discussion_end": max((p["created_at"] for p in matching_posts), default=None),
            },
            "votes": votes,
        }

        linked.append(joined)

    return linked

if __name__ == "__main__":
    proposals = load_jsonl("crawler_snapshot/data/proposals.jsonl")
    discourse = load_jsonl("crawler_dao/data/optimism_discourse_corpus.jsonl")
    votes = load_jsonl("crawler_snapshot/data/votes.jsonl")

    votes_by_pid = index_votes_by_proposal(votes)
    linked_data = link_discourse_and_votes(proposals, discourse, votes_by_pid)

    save_jsonl("./data/linked_proposals.jsonl", linked_data)
    print(f"✅ Linked {len(linked_data)} proposals and saved to linked_proposals.jsonl")
