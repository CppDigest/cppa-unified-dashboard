# Investigation Plan: C++ Repositories with Boost Usage (10+ Stars)

---

## Objective

To find **all** C++ repositories with more than 10 stars that use Boost, and keep that set updated over time.

**Rationale for two steps:** Step 1 monitors **content change** (recently pushed = code/commits changed). Step 2 monitors **star change** (repos that crossed the 10-star threshold—we find them by creation-date search and add those not yet in our list).

---

## Search Limitations (GitHub API)

- **Minimum range:** One day for `created` and `pushed`.
- **Result cap:** At most **1000 items** per query. Split ranges when count > 900.
- **Typical volumes:** Pushed (e.g. 3 days ago) ~**700–800**/day; created (e.g. a month in a past year) ~**500–600**/month. One-day pushed and monthly created are usually safe; split busy periods.

Success: over time the `repository` table and Boost-usage data cover all C++ repos with 10+ stars that we can retrieve within the 1000/query limit.

---

## Step 1: Monitor Content Change (Recently Pushed)

Among C++ repos with 10+ stars that were **pushed** recently (e.g. daily), find those that use Boost and update the global list.

- Query GitHub: `language:C++ stars:>10 pushed:YYYY-MM-DD..YYYY-MM-DD` with **one-day** ranges.
- Ensure each returned repo is in the `repository` table; update metadata (stars, `pushed_at`).
- Run Boost-detection (e.g. `#include <boost/` / `#include "boost/`) and persist usage.
- Use **`GitHubBoostSearcher.search_repos(start_date, end_date, stars_min=10)`** (already uses `pushed`, splits when >900). Drive from **`main_pipeline`** with `--since` / `--until`; then **`ingest_boost_usage`**.

---

## Step 2: Monitor Star Change (Backfill by Creation Date)

Find C++ repos **created** on past dates that **now have** 10+ stars and are not already in the list; check Boost usage.

- Query: `language:C++ stars:>10 created:YYYY-MM-DD..YYYY-MM-DD`. Use month or day windows; if a window’s count > 900, split it.
- Filter out repos already in `repository` (or already checked).
- Run Boost detection and ingest for the remainder. Repeat for other creation-date windows.
- Use same searcher with **`SEARCH_ACTION = "created"`**; **`generate_pushed_ranges`** uses 60-day steps for created—split window if it exceeds the API limit (e.g. **`count_items_from_git`** then sub-ranges).

---

## Strategy and Code

- **Step 1:** One-day `pushed` ranges; existing **`_process_date_range`** already splits when `total_count > 900`.
- **Step 2:** `created` with month/day ranges; call **`count_items_from_git`** and split if > 900; deduplicate against DB. Respect rate limits; keep runs idempotent (upsert repos and usage).

**Reuse:** `git_search.py` — `search_repos`, `generate_pushed_ranges`, `_process_date_range`, `count_items_from_git`, `ensure_tables_exist`; `main_pipeline.py` — `main` (--since/--until), `ingest_boost_usage`. Run report/dashboard after ingest to refresh the “all C++ 10+ stars + Boost” view.

**Data flow:** Step 1: Search (pushed/day) → update `repository` → Boost detection → usage/header tables → optional report/dashboard.
Step 2: Search (created/window) → exclude existing → Boost detection → ingest → optional report.

**Implementation:** Automate Step 1 (e.g. cron) with `main_pipeline --since YYYY-MM-DD --until YYYY-MM-DD` for the previous day.
Add a backfill script/mode for Step 2 with `SEARCH_ACTION=created`, configurable date range, and split-when-over-limit logic. Run Step 2 in off-peak hours if doing large backfills to ease rate limits.

**Caveats:** Very busy days (>1000/day) may miss some repos; split where possible. Long backfills may need multiple runs or a higher-rate-limit token. Optionally distinguish system vs vendored Boost in detection for the dashboard.

---
