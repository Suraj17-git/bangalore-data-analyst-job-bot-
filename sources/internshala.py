
import requests
from bs4 import BeautifulSoup
HEADERS = {'User-Agent':'Mozilla/5.0'}

def fetch_jobs(city_names, keywords):
    results = []
    try:
        for kw in keywords[:4]:
            q = '+'.join(kw.split())
            city_slug = city_names[0].lower().replace(' ', '-')
            url = f'https://internshala.com/internships/{q}-internship-in-{city_slug}'
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, 'html.parser')
            for div in soup.select('div.individual_internship')[:20]:
                title_el = div.select_one('a.internship_list_header')
                title = title_el.get_text(strip=True) if title_el else None
                link = 'https://internshala.com' + title_el.get('href') if title_el and title_el.get('href') else None
                company = div.select_one('.company_name a') and div.select_one('.company_name a').get_text(strip=True)
                results.append({'title': title, 'company': company, 'location': city_names[0], 'url': link, 'source': 'internshala', 'posted_date': None})
    except Exception as e:
        print('[warn] internshala fetch failed', e)
    return results
