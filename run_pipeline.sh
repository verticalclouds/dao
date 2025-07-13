#!/bin/bash

set -e

./run_backup.sh

# Run Discourse and Snapshot crawlers in parallel
(
    echo "▶️ Starting Discourse pipeline"
    /usr/bin/caffeinate -dimsu python ./crawler_dao/downloader_dao.py
    /usr/bin/caffeinate -dimsu python ./crawler_dao/main.py
    echo "✅ Discourse pipeline done"
) &

(
    echo "▶️ Starting Snapshot pipeline"
    /usr/bin/caffeinate -dimsu python ./crawler_snapshot/downloader_snapshot.py
    echo "✅ Snapshot pipeline done"
) &

# Wait for both background jobs to finish
wait

# Joiner and Scorecards
/usr/bin/caffeinate -dimsu python joiner.py
/usr/bin/caffeinate -dimsu python proposal_scorecards.py

echo "✅ pipeline executed"
