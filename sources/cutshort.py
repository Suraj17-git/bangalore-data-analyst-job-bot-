
import requests
from bs4 import BeautifulSoup
HEADERS = {'User-Agent':'Mozilla/5.0'}
def fetch_jobs(city_names, keywords):
    results = []
    try:
        q = '+'.join(keywords[0].split())
        url = f'https://cutshort.io/search?query={q}&location={city_names[0]}'
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.select('a.job-card')[:30]:
            title = a.select_one('.job-title') and a.select_one('.job-title').get_text(strip=True)
            company = a.select_one('.company-name') and a.select_one('.company-name').get_text(strip=True)
            link = a.get('href')
            results.append({'title': title, 'company': company, 'location': city_names[0], 'url': link, 'source': 'cutshort', 'posted_date': None})
    except Exception as e:
        print('[warn] cutshort fetch failed', e)
    return results
