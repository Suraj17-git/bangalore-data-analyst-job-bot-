
import logging
from bs4 import BeautifulSoup
from utils.retry import retry_with_backoff, safe_request

logger = logging.getLogger('job_bot')
HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

@retry_with_backoff(max_retries=3, initial_delay=2.0)
def fetch_jobs(city_names, keywords):
    results = []
    for kw in keywords[:4]:
        for city in city_names[:1]:
            q = '+'.join(kw.split())
            city_q = '+'.join(city.split())
            url = f'https://wellfound.com/jobs?search={q}&location={city_q}'
            try:
                logger.info(f"Querying Wellfound for: {kw} in {city}")
                r = safe_request(url, headers=HEADERS, timeout=20)
                soup = BeautifulSoup(r.text, 'html.parser')
                job_links = soup.select('a[data-cy="job-card-link"]')[:12]
                
                logger.info(f"Found {len(job_links)} job listings on Wellfound for {kw} in {city}")
                
                for a in job_links:
                    title = a.select_one('h3') and a.select_one('h3').get_text(strip=True)
                    company = a.select_one('h4') and a.select_one('h4').get_text(strip=True)
                    href = a.get('href')
                    link = 'https://wellfound.com' + href if href and href.startswith('/') else href
                    results.append({'title': title, 'company': company, 'location': city, 'url': link, 'source': 'wellfound', 'posted_date': None})
            except Exception as e:
                logger.error(f"Wellfound fetch failed for {kw} in {city}: {str(e)}")
    return results
