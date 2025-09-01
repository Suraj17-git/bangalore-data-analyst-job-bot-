
import requests
def fetch_jobs_for_company(company_career_url):
    results = []
    try:
        if 'lever.co' in company_career_url or 'jobs.lever.co' in company_career_url:
            api = company_career_url.rstrip('/') + '/positions'
            r = requests.get(api, timeout=20)
            if r.status_code == 200 and 'application/json' in r.headers.get('content-type',''):
                for p in r.json():
                    results.append({'title': p.get('text') or p.get('title'), 'company': p.get('categories',{}).get('team') or None, 'location': p.get('categories',{}).get('location'), 'url': p.get('hostedUrl') or p.get('applyUrl') or p.get('apply_url'), 'source': 'lever', 'posted_date': None})
            else:
                api2 = company_career_url.rstrip('/') + '/positions.json'
                r2 = requests.get(api2, timeout=20)
                if r2.status_code == 200:
                    for p in r2.json():
                        results.append({'title': p.get('title'), 'company': p.get('team'), 'location': p.get('location'), 'url': p.get('absolute_url'), 'source': 'lever', 'posted_date': None})
    except Exception as e:
        print('[warn] lever fetch failed for', company_career_url, e)
    return results
