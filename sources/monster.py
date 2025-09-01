import requests
from bs4 import BeautifulSoup
HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

def fetch_jobs(city_names, keywords):
    results = []
    try:
        for kw in keywords[:4]:
            q = '-'.join(kw.split())
            city_slug = city_names[0].lower().replace(' ', '-')
            url = f'https://www.monsterindia.com/srp/results?query={q}&locations={city_slug}'
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            for job in soup.select('div.card-apply-content')[:20]:
                title_el = job.select_one('div.job-tittle h3 a')
                title = title_el.get_text(strip=True) if title_el else None
                
                company_el = job.select_one('span.company-name a')
                company = company_el.get_text(strip=True) if company_el else None
                
                link_el = job.select_one('div.job-tittle h3 a')
                link = link_el.get('href') if link_el else None
                
                location_el = job.select_one('div.location-name span')
                location = location_el.get_text(strip=True) if location_el else city_names[0]
                
                results.append({
                    'title': title, 
                    'company': company, 
                    'location': location, 
                    'url': link, 
                    'source': 'monster', 
                    'posted_date': None
                })
    except Exception as e:
        print('[warn] Monster fetch failed', e)
    return results