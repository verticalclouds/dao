import json
from pathlib import Path
from datetime import datetime, timezone

def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def save_jsonl(path, items):
    with open(path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")

def extract_summary(body, max_len=280):
    if not body:
        return ""
    summary = " ".join(body.strip().splitlines())
    return summary[:max_len].rsplit(" ", 1)[0] + "..." if len(summary) > max_len else summary

def build_scorecard(proposal):
    prop_id = proposal["proposal_id"]
    space_id = proposal.get("space", {}).get("id", "unknown")
    discourse_url = None
    discourse_url = proposal.get("discourse_url")
    voting = proposal.get("voting", {})
    result = voting.get("result", {})
    voter_stats = voting.get("voter_stats", {})
    engagement = proposal.get("engagement", {})
    vote_percentages = normalize_to_percentages(result.get("vote_distribution", {}))

    return {
        "proposal_id": prop_id,
        "dao_space": space_id,
        "snapshot_url": f"https://snapshot.org/#/{space_id}/proposal/{prop_id}",
        "discourse_url": discourse_url,
        "title": proposal.get("title"),
        "author": proposal.get("snapshot_author"),
        "created_utc": proposal.get("created"),
        "summary": extract_summary(proposal.get("body", "")),

        "voting": {
            "type": voting.get("type"),
            "start_utc": voting.get("start_utc"),
            "end_utc": voting.get("end_utc"),
            "choices": voting.get("choices"),
            "result": {
                "winning_choice": result.get("winning_choice"),
                "total_voters": result.get("total_voters"),
                "total_voting_power": result.get("total_voting_power"),
                "turnout_percent": result.get("turnout_percent"),
                "vote_distribution": result.get("vote_distribution"),
            }
        },

        "engagement": {
            "discourse_post_count": engagement.get("discourse_post_count"),
            "unique_posters": engagement.get("unique_posters"),
            "discussion_start": engagement.get("discussion_start"),
            "discussion_end": engagement.get("discussion_end"),
        },

        "notable_behaviors": {
            "whale_support": detect_whales(proposal.get("votes", [])),
            "sybil_signals": {
                "num_low_vp_votes": voter_stats.get("low_vp_votes", 0),
                "threshold_vp": 0.01
            },
            "repeat_voters": voter_stats.get("voters_with_multiple_votes", 0),
            "controversy_score": calc_controversy(vote_percentages)
        },

        "status": "passed" if result.get("winning_choice") else "undecided"
    }

def detect_whales(votes, whale_threshold=500_000):
    return [
        v["voter"]
        for v in votes
        if v.get("vp", 0) >= whale_threshold
    ]

def normalize_to_percentages(vote_distribution):
    total = sum(vote_distribution.values())
    if total == 0:
        return {k: 0.0 for k in vote_distribution}
    return {k: (v / total) * 100 for k, v in vote_distribution.items()}

def calc_controversy(vote_percentages):
    if not vote_percentages or len(vote_percentages) < 2:
        return 0.0
    sorted_percents = sorted(vote_percentages.values(), reverse=True)
    top = sorted_percents[0]
    second = sorted_percents[1]
    return round(1 - abs(top - second) / 100, 4)

if __name__ == "__main__":
    proposals = load_jsonl("./data/linked_proposals.jsonl")
    scorecards = [build_scorecard(p) for p in proposals]
    save_jsonl("./data/scorecards_opcollective.jsonl", scorecards)
    print(f"✅ Generated {len(scorecards)} scorecards → scorecards_opcollective.jsonl")
