
import requests
from bs4 import BeautifulSoup
HEADERS = {'User-Agent':'Mozilla/5.0'}
def fetch_jobs(city_names, keywords):
    results = []
    try:
        r = requests.get('https://jobs.ycombinator.com/', headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        for tr in soup.select('tr.job')[:30]:
            title_el = tr.select_one('a.job-link')
            title = title_el.get_text(strip=True) if title_el else None
            link = title_el.get('href') if title_el else None
            company = tr.select_one('.company') and tr.select_one('.company').get_text(strip=True)
            results.append({'title': title, 'company': company, 'location': None, 'url': link, 'source': 'yc_jobs', 'posted_date': None})
    except Exception as e:
        print('[warn] yc jobs fetch failed', e)
    return results
