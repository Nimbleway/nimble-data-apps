# Consumer Sentiment Monitor

A Nimble data app for tracking launch sentiment around a product across social discussion, Reddit-style conversations, reviews/comparison pages, and news/blog coverage.

It uses Nimble's Search API:

```http
POST https://sdk.nimbleway.com/v1/search
Authorization: Bearer $NIMBLE_API_KEY
```

The app turns focused web searches into a structured launch-readiness report with source links, sentiment buckets, risks, and recommended follow-up searches.

## What it does

| Step | What happens | Nimble capability |
|---|---|---|
| 1 | Reads a product launch config and source plan | — |
| 2 | Searches social, Reddit/web/forum/review/news queries | Nimble Search API with `focus` modes |
| 3 | Saves every raw API response before parsing | Resumable raw cache |
| 4 | Normalizes results into one schema | App layer |
| 5 | Classifies lightweight sentiment and risk terms | App layer |
| 6 | Writes a structured report and Streamlit dashboard | App layer |

## Quickstart — sample dashboard, no API key

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

The dashboard loads `data/sample_run/` by default, so it works without any credentials.

## Run a dry-run collection

```bash
python3 collect.py --dry-run
streamlit run dashboard.py
```

Dry-run mode writes synthetic Nimble-shaped raw responses to `data/dry_run/`. This verifies the full cache → normalize → report pipeline without making external calls.

## Run with Nimble Search API

```bash
pip install -r requirements.txt
cp .env.example .env
# Add NIMBLE_API_KEY to .env
python3 collect.py --config config/example_config.json
streamlit run dashboard.py
```

Each live run is written to `data/runs/<timestamp>/`.

## Configure the launch monitor

Edit `config/example_config.json`:

```json
{
  "product_name": "Your Product",
  "launch_context": "What launched and who it is for.",
  "country": "US",
  "locale": "en-US",
  "search_depth": "fast",
  "include_answer": true,
  "max_results": 8,
  "queries": [
    {
      "id": "reddit_reactions",
      "label": "Reddit launch reactions",
      "focus": "social",
      "source_type": "reddit/social",
      "query": "Your Product launch Reddit user reactions objections pricing"
    }
  ]
}
```

Useful focus modes for this app:

- `social` — social and discussion-style results
- `news` — launch coverage and blogs
- `general` — reviews, comparisons, forums, docs, broader web
- `shopping` — retail/marketplace sentiment if the product is consumer or ecommerce-related

## Output files

Each run contains:

```text
report.json              # dashboard-ready executive summary and examples
normalized_results.json  # normalized source-linked records
schema.json              # normalized result schema
raw/*.json               # raw Nimble responses, saved before parsing
```

## Project structure

```text
consumer-sentiment-monitor/
├── collect.py
├── dashboard.py
├── config/
│   └── example_config.json
├── data/
│   └── sample_run/
│       ├── report.json
│       ├── normalized_results.json
│       ├── schema.json
│       └── raw/
├── requirements.txt
└── .env.example
```

## Notes

- The sentiment classifier is intentionally lightweight and transparent. It is good enough for a demo and easy to swap for Claude, OpenAI, or a Nimble-created analysis agent later.
- Raw responses are cached first. If parsing changes, reprocess the cached responses rather than burning another API run.
- Re-running against the same output directory skips existing raw responses.
