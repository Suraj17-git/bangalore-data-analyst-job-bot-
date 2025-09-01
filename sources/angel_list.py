
import requests
from bs4 import BeautifulSoup
HEADERS = {'User-Agent':'Mozilla/5.0'}

def fetch_jobs(city_names, keywords):
    results = []
    for kw in keywords[:4]:
        for city in city_names[:1]:
            q = '+'.join(kw.split())
            city_q = '+'.join(city.split())
            url = f'https://wellfound.com/jobs?search={q}&location={city_q}'
            try:
                r = requests.get(url, headers=HEADERS, timeout=20)
                r.raise_for_status()
                soup = BeautifulSoup(r.text, 'html.parser')
                for a in soup.select('a[data-cy="job-card-link"]')[:12]:
                    title = a.select_one('h3') and a.select_one('h3').get_text(strip=True)
                    company = a.select_one('h4') and a.select_one('h4').get_text(strip=True)
                    href = a.get('href')
                    link = 'https://wellfound.com' + href if href and href.startswith('/') else href
                    results.append({'title': title, 'company': company, 'location': city, 'url': link, 'source': 'wellfound', 'posted_date': None})
            except Exception as e:
                print('[warn] wellfound fetch failed', e)
    return results
