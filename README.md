# Google News API (Python) - search Google News by keyword, topic or city and get articles as JSON

Search **Google News** from Python and get structured results: headline, outlet, publish time, the real publisher URL and related coverage of the same story. This repo shows how to call the [Google News Scraper](https://apify.com/rel8ble/google-news-scraper) on Apify from Python and Node, plus a small media-monitoring script that compares how much coverage several brands got in the last week.

> Disclosure: I built this actor; it's a paid tool on Apify ($1.00 per 1,000 articles).

There is no official Google News API. The actor reads Google News' public RSS feeds over plain HTTP (no browser, no login, no API key) for any language and country edition, and can decode the `news.google.com/rss/articles/...` links into the article's own address.

## What you can do with it

- **Share of voice.** Put your brand and two competitors in as queries with a 7-day window and count articles and distinct outlets per name.
- **Ticker and crypto news feeds.** Run `1h` or `1d` searches on a schedule and push new headlines to Slack or a database; `articleId` is stable, so deduplication is exact.
- **Outlet lists for PR.** See which publications actually write about a topic, ranked by article count.
- **Historical research.** `dateFrom` / `dateTo` restrict a search to a fixed window, years back.
- **Feeding an LLM or RAG pipeline.** Dated, sourced headlines plus a resolved URL you can hand to a text extractor.

## Quick start (Python)

```bash
pip install apify-client
```

```python
from apify_client import ApifyClient

client = ApifyClient("<YOUR_APIFY_TOKEN>")

run = client.actor("rel8ble/google-news-scraper").call(run_input={
    "queries": ["openai"],
    "timeRange": "7d",
    "maxItemsPerQuery": 100,
    "resolveUrls": True,
})

for a in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(a["publishedAt"][:10], "|", a["sourceName"], "|", a["title"])
    print("   ", a["url"])
```

Your token is at https://console.apify.com/settings/integrations.

## Quick start (Node.js)

```js
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: '<YOUR_APIFY_TOKEN>' });

const run = await client.actor('rel8ble/google-news-scraper').call({
    topics: ['TECHNOLOGY'],
    language: 'en-GB',
    country: 'GB',
    maxItemsPerQuery: 50,
});

const { items } = await client.dataset(run.defaultDatasetId).listItems();
for (const a of items) console.log(a.sourceName, '-', a.title, `(${a.relatedCount} related)`);
```

## Full example: weekly share of voice

[`example.py`](example.py) runs several queries over the past 7 days with link decoding on, then writes `news.csv` and prints, per query: article count, distinct outlets, the top outlets and the busiest day. It also lists outlets that covered more than one of the names.

```bash
pip install -r requirements.txt
export APIFY_TOKEN=<YOUR_APIFY_TOKEN>      # Windows: set APIFY_TOKEN=...
python example.py tesla openai "nvidia earnings"
```

Real numbers from one run (US edition, 150 articles per query, 4-11 Oct 2026):

| Query | Articles | Distinct outlets | Top 3 outlets |
|---|---|---|---|
| tesla | 150 | 72 | Yahoo Finance (21), Not a Tesla App (14), Teslarati (9) |
| openai | 150 | 76 | OpenAI (17), The New York Times (7), Reuters (7) |
| nvidia earnings | 150 | 55 | The Globe and Mail (20), Stocktwits (17), 24/7 Wall St. (12) |

All 450 links in that run were decoded to the publisher's own URL. The same run's Technology topic feed (65 articles from 46 outlets) had related coverage on 56 rows.

## Input

| Field | What it does |
|---|---|
| `queries` | Search terms as you'd type them on news.google.com: `tesla`, `"climate change" -opinion`, `nvidia OR amd earnings` |
| `topics` | Google News sections: `TOP`, `WORLD`, `NATION`, `BUSINESS`, `TECHNOLOGY`, `ENTERTAINMENT`, `SPORTS`, `SCIENCE`, `HEALTH` |
| `locations` | Local news for a place: `Chicago`, `Bavaria`, `Sydney` |
| `language` / `country` | Edition, e.g. `en-US` / `US`, `de` / `DE`, `pt-BR` / `BR` |
| `timeRange` | `anytime`, `1h`, `12h`, `1d`, `7d`, `30d`, `1y` |
| `dateFrom` / `dateTo` | Exact window as `YYYY-MM-DD`; overrides `timeRange` |
| `sites` | Only these publishers: `reuters.com`, `bbc.com` |
| `maxItemsPerQuery` | Articles per query, topic or place (default 100). Above 100 needs a time window: the actor then searches day by day |
| `resolveUrls` | `true` decodes Google links to the publisher's URL (no extra charge) |

## Output (real row, trimmed)

From the Technology topic feed, 11 Oct 2026:

```json
{
  "position": 2,
  "title": "MacBook Pro overhaul: entry-level model to gain new design sooner than expected",
  "sourceName": "9to5Mac",
  "sourceUrl": "https://9to5mac.com",
  "publishedAt": "2026-10-11T04:25:00.000Z",
  "url": "https://9to5mac.com/2026/10/10/m7-macbook-pro-redesign-next-spring/",
  "publisherUrl": "https://9to5mac.com/2026/10/10/m7-macbook-pro-redesign-next-spring/",
  "urlResolved": true,
  "relatedArticles": [
    { "title": "Apple Set to Debut Touch-Screen MacBook and New iPad Mini in Late October", "sourceName": "Bloomberg.com" },
    { "title": "Apple to launch touchscreen MacBook and iPad mini in October", "sourceName": "Mashable" }
  ],
  "relatedCount": 4,
  "feedType": "topic",
  "topic": "TECHNOLOGY",
  "language": "en-US",
  "country": "US"
}
```

Rows also carry `articleId`, `googleNewsUrl`, `query`, `location`, `searchQuery` (the exact text sent, with `site:` / `when:` operators), `feedUrl` and `scrapedAt`.

## Pricing

$1.00 per 1,000 articles, pay per result. No start fee, and decoding publisher URLs costs nothing extra. Apify's free plan credit covers a few thousand articles to try it.

## Limits

- Headlines only: Google News feeds carry no article body, author or image. Pass `publisherUrl` to an article extractor if you need the text.
- One Google News request returns about 100 articles at most; going higher needs a `timeRange` or date window so the actor can split by day.
- Older articles often have only a date from Google (time shows 07:00 or 08:00 UTC).
- The same query returns different outlets per edition (`US` vs `GB`).
- If a link can't be decoded the row is kept with `urlResolved: false` and the Google link in `url`.

## Links

- Actor on the Apify Store: https://apify.com/rel8ble/google-news-scraper
- Other scrapers by the same author: https://apify.com/rel8ble

## License

MIT for the code in this repo. Using the data is your responsibility under Google's and the publishers' terms.
