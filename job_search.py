
import os, json, time, html
from datetime import datetime
from dotenv import load_dotenv
from utils.emailer import send_email
from utils.normalize import normalize_text
import pandas as pd

load_dotenv()

CITY_NAMES = [c.strip() for c in os.getenv("CITY_NAMES","Bangalore,Bengaluru").split(",") if c.strip()]
QUERY_KEYWORDS = [q.strip() for q in os.getenv("QUERY_KEYWORDS","Entry Level Data Analyst,Data Analyst Intern,Junior Data Analyst,Data Analytics Intern,Data Science Intern").split(",") if q.strip()]
SAVE_HTML = os.getenv("SAVE_HTML","1") == "1"
OUTPUT_DIR = os.getenv("OUTPUT_DIR","out")

from sources import google_serpapi, angel_list, yc_jobs, internshala, naukri, cutshort, lever, greenhouse, workable, linkedin, indeed, glassdoor, monster

def fetch_all():
    jobs = []
    jobs.extend(google_serpapi.fetch_jobs(CITY_NAMES, QUERY_KEYWORDS) or [])
    jobs.extend(angel_list.fetch_jobs(CITY_NAMES, QUERY_KEYWORDS) or [])
    jobs.extend(yc_jobs.fetch_jobs(CITY_NAMES, QUERY_KEYWORDS) or [])
    jobs.extend(internshala.fetch_jobs(CITY_NAMES, QUERY_KEYWORDS) or [])
    jobs.extend(naukri.fetch_jobs(CITY_NAMES, QUERY_KEYWORDS) or [])
    jobs.extend(cutshort.fetch_jobs(CITY_NAMES, QUERY_KEYWORDS) or [])
    jobs.extend(linkedin.fetch_jobs(CITY_NAMES, QUERY_KEYWORDS) or [])
    jobs.extend(indeed.fetch_jobs(CITY_NAMES, QUERY_KEYWORDS) or [])
    jobs.extend(glassdoor.fetch_jobs(CITY_NAMES, QUERY_KEYWORDS) or [])
    jobs.extend(monster.fetch_jobs(CITY_NAMES, QUERY_KEYWORDS) or [])
    try:
        with open('company_careers.json','r') as f:
            cc = json.load(f)
        for c in cc.get('companies', []):
            url = c.get('careers')
            if not url:
                continue
            jobs += lever.fetch_jobs_for_company(url) or []
            jobs += greenhouse.fetch_jobs_for_company(url) or []
            jobs += workable.fetch_jobs_for_company(url) or []
    except Exception as e:
        print('[warn] company_careers.json not loaded or parsing failed', e)
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
    print('[info] fetching jobs from sources...')
    raw = fetch_all()
    print(f'[info] raw count: {len(raw)}')
    jobs = dedupe_and_rank(raw)
    print(f'[info] after dedupe & rank: {len(jobs)}')
    html_body = to_html(jobs)
    subject = 'Bangalore Data Analyst — Daily Job Scan'
    if SAVE_HTML:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M')
        path = os.path.join(OUTPUT_DIR, f'jobs_{ts}.html')
        with open(path,'w',encoding='utf-8') as f:
            f.write(html_body)
        print('[info] saved HTML ->', path)
    send_email(subject, html_body)
    print('[info] done.')

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--once', action='store_true')
    args = p.parse_args()
    main(run_once=args.once)
