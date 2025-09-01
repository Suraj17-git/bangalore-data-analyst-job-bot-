
import requests
from bs4 import BeautifulSoup
HEADERS = {'User-Agent':'Mozilla/5.0'}
def fetch_jobs(city_names, keywords):
    results = []
    try:
        for kw in keywords[:4]:
            q = '-'.join(kw.split())
            city_slug = city_names[0].lower().replace(' ', '-')
            url = f'https://www.naukri.com/{q}-jobs-in-{city_slug}'
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            for div in soup.select('article.jobTuple')[:30]:
                title = div.select_one('a.title') and div.select_one('a.title').get_text(strip=True)
                company = div.select_one('a.subTitle') and div.select_one('a.subTitle').get_text(strip=True)
                link = div.select_one('a.title') and div.select_one('a.title').get('href')
                results.append({'title': title, 'company': company, 'location': city_names[0], 'url': link, 'source': 'naukri', 'posted_date': None})
    except Exception as e:
        print('[warn] naukri fetch failed', e)
    return results
