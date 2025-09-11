import time
import random
import logging
import functools
import requests
from typing import Callable, Any, Dict, List, Optional, Union, TypeVar

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('job_bot')

# Type variable for generic function return type
T = TypeVar('T')

def retry_with_backoff(max_retries: int = 3, 
                      initial_delay: float = 1.0,
                      backoff_factor: float = 2.0,
                      jitter: bool = True,
                      retryable_exceptions: tuple = (requests.RequestException,
                                                    ConnectionError,
                                                    TimeoutError)):
    """
    Decorator that retries a function with exponential backoff when specified exceptions occur.
    
    Args:
        max_retries: Maximum number of retries before giving up
        initial_delay: Initial delay between retries in seconds
        backoff_factor: Multiplier applied to delay between retries
        jitter: Whether to add randomness to the delay
        retryable_exceptions: Tuple of exceptions that trigger a retry
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Union[T, List]]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Union[T, List]:
            delay = initial_delay
            last_exception = None
            source_name = kwargs.get('source_name', func.__name__)
            
            for retry in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if retry >= max_retries:
                        logger.error(f"[{source_name}] Failed after {max_retries} retries: {str(e)}")
                        break
                    
                    # Calculate delay with optional jitter
                    jitter_value = random.uniform(0.8, 1.2) if jitter else 1.0
                    current_delay = delay * jitter_value
                    
                    logger.warning(f"[{source_name}] Attempt {retry+1}/{max_retries} failed: {str(e)}. Retrying in {current_delay:.2f}s")
                    time.sleep(current_delay)
                    delay *= backoff_factor
                except Exception as e:
                    # Non-retryable exception
                    logger.error(f"[{source_name}] Non-retryable error: {str(e)}")
                    last_exception = e
                    break
            
            # If we get here, all retries failed
            logger.error(f"[{source_name}] All attempts failed: {str(last_exception)}")
            return []
        
        return wrapper
    return decorator


def safe_request(url: str, 
                method: str = 'get', 
                timeout: int = 30, 
                max_retries: int = 3, 
                headers: Optional[Dict] = None, 
                **kwargs) -> requests.Response:
    """
    Makes a request with retry logic and proper error handling.
    
    Args:
        url: The URL to request
        method: HTTP method (get, post, etc.)
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries
        headers: HTTP headers
        **kwargs: Additional arguments to pass to requests
        
    Returns:
        Response object if successful
        
    Raises:
        requests.RequestException: If all retries fail
    """
    if headers is None:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    session = requests.Session()
    retry_strategy = requests.adapters.Retry(
        total=max_retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
    )
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    try:
        response = getattr(session, method.lower())(url, headers=headers, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.SSLError as e:
        logger.error(f"SSL Error for {url}: {str(e)}")
        raise
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection Error for {url}: {str(e)}")
        raise
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout Error for {url}: {str(e)}")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error for {url}: {str(e)}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Request Error for {url}: {str(e)}")
        raise
    finally:
        session.close()