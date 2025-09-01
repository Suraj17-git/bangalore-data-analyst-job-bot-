
import requests
from bs4 import BeautifulSoup
HEADERS = {'User-Agent':'Mozilla/5.0'}
from urllib.parse import urljoin
def fetch_jobs_for_company(company_career_url):
    results = []
    try:
        r = requests.get(company_career_url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.select('a[href*="/jobs/"]')[:60]:
            title = a.get_text(strip=True)
            link = a.get('href')
            if link and link.startswith('/'):
                link = urljoin(company_career_url, link)
            results.append({'title': title, 'company': None, 'location': None, 'url': link, 'source':'workable', 'posted_date': None})
    except Exception as e:
        print('[warn] workable fetch failed for', company_career_url, e)
    return results
