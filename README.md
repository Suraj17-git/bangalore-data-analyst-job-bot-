
# Bangalore Data Analyst Job Bot — Full Restore

This package restores the full implementation of the job aggregator with many source scrapers.
- SerpAPI (requires SERPAPI_KEY)
- Wellfound (AngelList) scraping
- YC Jobs scraping
- Internshala (requests-based; Playwright recommended)
- Naukri (requests-based; Playwright recommended)
- Cutshort scraping
- Lever JSON parsing for company career pages
- Greenhouse JSON parsing for company career pages
- Workable parsing for company pages
- Orchestrator that normalizes, dedupes, ranks, saves HTML, and emails via SMTP

Quickstart:
1. Copy `.env.example` → `.env` and fill keys (SERPAPI_KEY and SMTP settings if you want email).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # Optional for Playwright JS scraping:
   playwright install
   ```
3. Run once:
   ```bash
   python job_search.py --once
   ```
