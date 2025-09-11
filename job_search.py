
import os, json, time, html, logging
from datetime import datetime
from dotenv import load_dotenv
from utils.emailer import send_email
from utils.normalize import normalize_text
from utils.retry import retry_with_backoff
import pandas as pd

load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.getenv("OUTPUT_DIR", "out"), "job_bot.log"), mode='a')
    ]
)
logger = logging.getLogger('job_bot')

CITY_NAMES = [c.strip() for c in os.getenv("CITY_NAMES","Bangalore,Bengaluru").split(",") if c.strip()]
QUERY_KEYWORDS = [q.strip() for q in os.getenv("QUERY_KEYWORDS","Data Analyst Fresher,Data Analyst Intern,Junior Data Analyst,Entry Level Data Analyst,Data Analytics Fresher,Data Analytics Intern,Data Science Intern,Fresher Data Analyst,Data Analyst Trainee").split(",") if q.strip()]
SAVE_HTML = os.getenv("SAVE_HTML","1") == "1"
OUTPUT_DIR = os.getenv("OUTPUT_DIR","out")

from sources import google_serpapi, angel_list, yc_jobs, internshala, naukri, cutshort, lever, greenhouse, workable, linkedin, indeed, glassdoor, monster

@retry_with_backoff(max_retries=2, initial_delay=1.0)
def fetch_source(source_module, source_name, *args, **kwargs):
    """Fetch jobs from a source with proper error handling"""
    try:
        logger.info(f"Fetching jobs from {source_name}...")
        results = source_module.fetch_jobs(*args, **kwargs) or []
        logger.info(f"Found {len(results)} jobs from {source_name}")
        return results
    except Exception as e:
        logger.error(f"Error fetching from {source_name}: {str(e)}")
        return []

def fetch_all():
    jobs = []
    sources = [
        (google_serpapi, "SerpAPI"),
        (angel_list, "Wellfound/AngelList"),
        (yc_jobs, "YC Jobs"),
        (internshala, "Internshala"),
        (naukri, "Naukri"),
        (cutshort, "Cutshort"),
        (linkedin, "LinkedIn"),
        (indeed, "Indeed"),
        (glassdoor, "Glassdoor"),
        (monster, "Monster")
    ]
    
    for source_module, source_name in sources:
        try:
            results = fetch_source(source_module, source_name, CITY_NAMES, QUERY_KEYWORDS)
            jobs.extend(results)
        except Exception as e:
            logger.error(f"Failed to fetch from {source_name}: {str(e)}")
    
    # Handle company career pages
    try:
        with open('company_careers.json','r') as f:
            cc = json.load(f)
        
        for c in cc.get('companies', []):
            company_name = c.get('name', 'Unknown')
            url = c.get('careers')
            if not url:
                continue
                
            try:
                logger.info(f"Checking {company_name} careers page at {url}")
                lever_jobs = lever.fetch_jobs_for_company(url) or []
                greenhouse_jobs = greenhouse.fetch_jobs_for_company(url) or []
                workable_jobs = workable.fetch_jobs_for_company(url) or []
                
                jobs.extend(lever_jobs)
                jobs.extend(greenhouse_jobs)
                jobs.extend(workable_jobs)
                
                logger.info(f"Found {len(lever_jobs) + len(greenhouse_jobs) + len(workable_jobs)} jobs from {company_name}")
            except Exception as e:
                logger.error(f"Error fetching jobs for company {company_name}: {str(e)}")
    except Exception as e:
        logger.error(f"company_careers.json not loaded or parsing failed: {str(e)}")
    
    logger.info(f"Total jobs fetched from all sources: {len(jobs)}")
    return jobs

def normalize_job(raw):
    return {
        "title": raw.get("title") or raw.get("job_title") or "",
        "company": raw.get("company") or "",
        "location": raw.get("location") or "",
        "url": raw.get("url") or raw.get("link") or "",
        "source": raw.get("source") or "unknown",
        "posted_date": raw.get("posted_date")
    }

def dedupe_and_rank(jobs):
    df = pd.DataFrame([normalize_job(j) for j in jobs])
    if df.empty:
        return []
    df['key'] = df['title'].fillna('') + '||' + df['company'].fillna('')
    df['key_norm'] = df['key'].apply(lambda s: normalize_text(s))
    df = df.drop_duplicates(subset=['key_norm'])
    def score_row(r):
        s = 0.0
        src = (r.get('source') or '').lower()
        if any(x in src for x in ['wellfound','angel','lever','greenhouse','cutshort','workable','serpapi']):
            s += 3.0
        if 'intern' in (r.get('title') or '').lower() or 'entry' in (r.get('title') or '').lower():
            s += 1.0
        if 'bangalore' in (r.get('location') or '').lower() or 'bengaluru' in (r.get('location') or '').lower():
            s += 0.5
        return s
    df['score'] = df.apply(score_row, axis=1)
    df = df.sort_values(by=['score'], ascending=False)
    return df.to_dict('records')

def to_html(jobs):
    rows = []
    for j in jobs:
        rows.append(f"""
        <tr>
          <td style='padding:10px;border-bottom:1px solid #eee;'>
            <a href='{html.escape(j.get('url') or '')}' target='_blank'>{html.escape(j.get('title') or '')}</a><br/>
            <small>{html.escape(j.get('company') or '')} — {html.escape(j.get('location') or '')} • {html.escape(j.get('source') or '')}</small>
          </td>
        </tr>
        """)
    body = f"""
    <div style='font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;'>
      <h2>Bangalore Data Analyst — Aggregated Daily Scan</h2>
      <div>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
      <table width='100%' style='border-collapse:collapse;'>{''.join(rows) if rows else '<tr><td>No results found today.</td></tr>'}</table>
    </div>
    """
    return body

def main(run_once=False):
    try:
        logger.info('Starting job search process')
        logger.info('Fetching jobs from sources...')
        raw = fetch_all()
        logger.info(f'Raw job count: {len(raw)}')
        
        jobs = dedupe_and_rank(raw)
        logger.info(f'After deduplication and ranking: {len(jobs)}')
        
        html_body = to_html(jobs)
        subject = 'Bangalore Data Analyst — Daily Job Scan'
        
        if SAVE_HTML:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            ts = datetime.now().strftime('%Y%m%d_%H%M')
            path = os.path.join(OUTPUT_DIR, f'jobs_{ts}.html')
            with open(path,'w',encoding='utf-8') as f:
                f.write(html_body)
            logger.info(f'Saved HTML report to {path}')
        
        try:
            send_email(subject, html_body)
            logger.info('Email notification sent successfully')
        except Exception as e:
            logger.error(f'Failed to send email: {str(e)}')
        
        logger.info('Job search process completed successfully')
    except Exception as e:
        logger.error(f'Error in main process: {str(e)}')
        raise

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--once', action='store_true')
    args = p.parse_args()
    main(run_once=args.once)
