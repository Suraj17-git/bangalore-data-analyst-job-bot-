
import os, time, logging
import requests
from utils.retry import retry_with_backoff, safe_request

logger = logging.getLogger('job_bot')
SERPAPI_KEY = os.getenv('SERPAPI_KEY','').strip()

@retry_with_backoff(max_retries=3, initial_delay=2.0)
def fetch_jobs(city_names, query_keywords, max_results=12):
    if not SERPAPI_KEY:
        logger.warning('SERPAPI_KEY not configured, skipping SerpAPI source')
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
            logger.info(f"Querying SerpAPI for: {q}")
            r = safe_request('https://serpapi.com/search', params=params, timeout=30)
            data = r.json()
            
            job_count = len(data.get('organic_results', []))
            logger.info(f"Found {job_count} results from SerpAPI for query: {q}")
            
            for item in data.get('organic_results', []):
                results.append({
                    'title': item.get('title'),
                    'company': None,
                    'location': city_names[0] if city_names else None,
                    'url': item.get('link'),
                    'source': 'serpapi',
                    'posted_date': None
                })
        except requests.exceptions.RequestException as e:
            logger.error(f"SerpAPI request failed for query '{q}': {str(e)}")
        except ValueError as e:
            logger.error(f"SerpAPI JSON parsing failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in SerpAPI query: {str(e)}")
        
        # Add delay between requests to avoid rate limiting
        time.sleep(0.5)
    
    return results
