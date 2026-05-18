# Nimble Data App Best Practices

Activate automatically when the user is starting a new Nimble data app, collection script, or extraction pipeline. Work through this checklist in order. Enforce it — don't skip steps, and prompt the user at each gate before moving on.

## 1. Test Inline First

Before writing any script, run at least one real API call inline through the MCP integration or CLI. Confirm:
- The response keys match what the parser will expect
- The driver tier gets through (no challenge page, no empty result)
- The right tool is being used (agent vs. extract vs. batch)

**Gate**: Don't scaffold collection code until one successful inline call has been made.

## 2. Confirm Tool Selection

Ask explicitly:
- Is the target site static or JS-rendered? (`vx6` vs. `vx10` / `vx10-pro`)
- Does a pre-built agent exist for this platform? If yes, use it — don't write a parser.
- How many URLs? If more than ~20, `extract_batch` not a loop.
- Will this use the SDK or raw `requests`? For browser-session agents (AI platforms, authenticated interfaces), SDK is required.

## 3. Define the Schema First

Before any fetch code: get the full field list agreed, with types and sources. If pulling from multiple sources, normalize to a single shape before anything leaves the collection layer. Missing field or naming mismatch discovered mid-run means a re-fetch.

```python
SCHEMA = {
    "source":     str,
    "url":        str,
    "price":      int,   # cents
    "title":      str,
    "fetched_at": str,   # ISO timestamp
}
```

**Gate**: Schema must be defined before writing the first fetch function.

## 4. Save Raw Before Transforming

Every collection function must write the raw API response to disk immediately on receipt — before any parsing, transformation, or scoring. Tag the format at collection time (structured/freeform, HTML/markdown).

When analysis logic breaks later, reprocessing cached responses takes seconds. Re-fetching takes hours.

## 5. Make Scripts Resumable

Any loop over multiple items must check a cache before making a call. Skip if already fetched. Save immediately when a response arrives. A crash loses only the calls in flight — a re-run picks up where things stopped.

```python
def already_cached(item_id):
    path = RESPONSES_DIR / f"{item_id}.json"
    return path.exists()

pending = [item for item in all_items if not already_cached(item["id"])]
```

**Flag**: If the user writes a loop with no cache check, stop and add one before continuing.

## 6. Add a Monitor Thread

Any script running more than a handful of calls needs a background monitor: progress count, in-flight call list, soft warning threshold for slow calls. A script with no output is indistinguishable from a stuck script.

**Flag**: If a long-running job has no progress logging, add one before the script is considered done.

## 7. Use Batch for Scale

For more than ~20 URLs, switch to `extract_batch`. Up to 1,000 URLs in parallel, single request, `batch_id` returned immediately. Add S3 delivery for jobs that run longer than a few minutes. Add `callback_url` alongside `storage_url` to eliminate the polling loop entirely.

**Prompt**: Ask the user for their URL count before finalizing the collection architecture.

## 8. Use AI for Semantic Problems

Rule-based matching breaks on real data. If the task involves scoring equivalence, extracting a position from prose, or normalizing freeform text — use a language model. Claude Haiku handles these tasks well at low cost.

Use regex and string matching for structural extraction (field splitting, known formats). Use LLMs for interpretation (equivalence, position, normalization).

---

## Quick Reference

| Step | Gate / Flag |
|---|---|
| Inline test | No script until one real call succeeds |
| Tool selection | Confirm driver tier, agent vs. extract, SDK vs. requests |
| Schema | Define before first fetch function |
| Save raw | Write to disk before any transformation |
| Resumable | Cache check in every loop |
| Monitor | Progress logging on any long-running job |
| Batch | extract_batch for > ~20 URLs |
| AI labeling | LLM for semantic judgment, regex for structure |
