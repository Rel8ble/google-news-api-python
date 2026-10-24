"""Weekly Google News share of voice for a few names.

Usage:
    pip install -r requirements.txt
    set APIFY_TOKEN=<YOUR_APIFY_TOKEN>   (or export on macOS/Linux)
    python example.py tesla openai "nvidia earnings"

Writes news.csv and prints articles, distinct outlets, top outlets and the
busiest day per query, plus outlets that covered more than one name.
"""
import csv
import os
import sys
from collections import Counter, defaultdict

from apify_client import ApifyClient

ACTOR = "rel8ble/google-news-scraper"


def main():
    queries = sys.argv[1:] or ["tesla", "openai", "nvidia earnings"]
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("Set APIFY_TOKEN first (https://console.apify.com/settings/integrations)")

    client = ApifyClient(token)
    run = client.actor(ACTOR).call(run_input={
        "queries": queries,
        "language": "en-US",
        "country": "US",
        "timeRange": "7d",
        "maxItemsPerQuery": 150,
        "resolveUrls": True,
    })
    rows = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    if not rows:
        sys.exit("No articles returned.")

    fields = ["query", "publishedAt", "sourceName", "title", "url", "urlResolved", "articleId"]
    with open("news.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"Saved {len(rows)} articles to news.csv\n")

    by_query = defaultdict(list)
    for r in rows:
        by_query[r.get("query") or r.get("topic") or r.get("location")].append(r)

    outlet_names = defaultdict(set)
    for q, items in by_query.items():
        outlets = Counter(r["sourceName"] for r in items if r.get("sourceName"))
        days = Counter((r.get("publishedAt") or "")[:10] for r in items)
        day, day_n = days.most_common(1)[0]
        top = ", ".join(f"{name} ({n})" for name, n in outlets.most_common(3))
        print(f"{q}: {len(items)} articles from {len(outlets)} outlets; busiest day {day} ({day_n})")
        print(f"    top outlets: {top}")
        for name in outlets:
            outlet_names[name].add(q)

    shared = sorted(((n, qs) for n, qs in outlet_names.items() if len(qs) > 1),
                    key=lambda x: (-len(x[1]), x[0]))
    if shared:
        print("\nOutlets covering more than one name:")
        for name, qs in shared[:15]:
            print(f"    {name}: {', '.join(sorted(qs))}")


if __name__ == "__main__":
    main()
