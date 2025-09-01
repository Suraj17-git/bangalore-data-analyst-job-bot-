
import requests
def fetch_jobs_for_company(company_career_url):
    results = []
    try:
        json_url = company_career_url.rstrip('/') + '/jobs.json'
        r = requests.get(json_url, timeout=20)
        if r.status_code == 200:
            data = r.json()
            for j in data.get('jobs', []):
                loc = j.get('location')
                if isinstance(loc, dict):
                    loc_name = loc.get('name')
                else:
                    loc_name = loc
                results.append({'title': j.get('title'), 'company': data.get('company',{}).get('name') or None, 'location': loc_name, 'url': j.get('absolute_url'), 'source':'greenhouse', 'posted_date': None})
    except Exception as e:
        print('[warn] greenhouse fetch failed for', company_career_url, e)
    return results
