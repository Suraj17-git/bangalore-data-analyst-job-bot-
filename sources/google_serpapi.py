
import os, requests, time
SERPAPI_KEY = os.getenv('SERPAPI_KEY','').strip()
def fetch_jobs(city_names, query_keywords, max_results=12):
    if not SERPAPI_KEY:
        return []
    queries = []
    for city in city_names:
        for q in query_keywords[:6]:
            queries.append(f'"{q}" {city}')
    results = []
    for q in queries:
        params = {
            'engine': 'google',
            'q': q,
            'api_key': SERPAPI_KEY,
            'num': max_results
        }
        try:
            r = requests.get('https://serpapi.com/search', params=params, timeout=30)
            r.raise_for_status()
            data = r.json()
            for item in data.get('organic_results', []):
                results.append({
                    'title': item.get('title'),
                    'company': None,
                    'location': city_names[0] if city_names else None,
                    'url': item.get('link'),
                    'source': 'serpapi',
                    'posted_date': None
                })
        except Exception as e:
            print('[warn] serpapi query failed', e)
        time.sleep(0.5)
    return results
