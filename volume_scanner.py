import time
import requests
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import pytz

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('volume_scanner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
API_KEY = os.getenv("FINNHUB_API_KEY", "YOUR_FINNHUB_API_KEY")
WATCHLIST = ["NOK", "LNOK", "AAPL", "TSLA", "NVDA", "AMD"]
RVOL_THRESHOLD = 1.5  # 50% above 20-day average
SCAN_INTERVAL = 120   # 2 minutes
MAX_RETRIES = 3
RETRY_DELAY = 2       # seconds

# API endpoints
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"
QUOTE_ENDPOINT = f"{FINNHUB_BASE_URL}/quote"
NEWS_ENDPOINT = f"{FINNHUB_BASE_URL}/company-news"

# Control file for start/stop
CONTROL_FILE = "scanner_control.txt"
PREVIOUS_ALERTS_FILE = "previous_alerts.txt"

# Time zone for pre-market check
PST = pytz.timezone('America/Los_Angeles')

# News keywords to filter for catalyst detection
CATALYST_KEYWORDS = [
    'earnings', 'contract', 'fda', 'approval', 'acquisition', 
    'merger', 'partnership', 'deal', 'patent', 'lawsuit', 
    'innovation', 'breakthrough', 'revenue', 'guidance'
]

# --- ERROR CLASSES ---
class FinnhubAPIError(Exception):
    """Raised when Finnhub API returns an error"""
    pass

class DataValidationError(Exception):
    """Raised when data validation fails"""
    pass

# --- UTILITY FUNCTIONS ---
def is_market_hours():
    """Check if current time is between 4am-9am PST (pre-market)"""
    try:
        current_time = datetime.now(PST)
        market_open = current_time.replace(hour=4, minute=0, second=0, microsecond=0)
        market_close = current_time.replace(hour=9, minute=0, second=0, microsecond=0)
        return market_open <= current_time <= market_close
    except Exception as e:
        logger.error(f"Error checking market hours: {e}")
        return False

def control_file_exists():
    """Check if control file exists (acts as 'run' button)"""
    return os.path.exists(CONTROL_FILE)

def load_previous_alerts() -> set:
    """Load previously alerted symbols to avoid duplicates"""
    try:
        if os.path.exists(PREVIOUS_ALERTS_FILE):
            with open(PREVIOUS_ALERTS_FILE, 'r') as f:
                return set(line.strip() for line in f.readlines())
    except Exception as e:
        logger.warning(f"Could not load previous alerts: {e}")
    return set()

def save_alert(symbol: str):
    """Save alert to prevent duplicate alerts in same session"""
    try:
        with open(PREVIOUS_ALERTS_FILE, 'a') as f:
            f.write(f"{symbol}\n")
    except Exception as e:
        logger.error(f"Could not save alert for {symbol}: {e}")

def make_api_request(url: str, params: Dict, retries: int = MAX_RETRIES) -> Dict:
    """
    Make API request with retry logic and error handling
    
    Args:
        url: API endpoint URL
        params: Query parameters
        retries: Number of retry attempts
        
    Returns:
        Response JSON dictionary
        
    Raises:
        FinnhubAPIError: If API call fails after retries
    """
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            
            # Check for rate limiting
            if response.status_code == 429:
                wait_time = int(response.headers.get('X-Ratelimit-Reset', 60))
                logger.warning(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            # Check for other HTTP errors
            response.raise_for_status()
            
            data = response.json()
            
            # Check if response contains error field
            if 'error' in data:
                raise FinnhubAPIError(f"API Error: {data['error']}")
            
            return data
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt + 1}/{retries}")
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY)
                
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error on attempt {attempt + 1}/{retries}: {e}")
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise FinnhubAPIError(f"Request failed: {e}")
        
        except ValueError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise FinnhubAPIError(f"Invalid response format: {e}")
    
    raise FinnhubAPIError(f"Max retries exceeded for {url}")

# --- CORE SCANNER FUNCTIONS ---
def get_current_volume(symbol: str) -> Optional[float]:
    """
    Fetch current volume from Finnhub quote data
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Current volume as float, or None if error
    """
    try:
        if not API_KEY or API_KEY == "YOUR_FINNHUB_API_KEY":
            logger.error("API key not configured. Set FINNHUB_API_KEY environment variable.")
            return None
        
        params = {'symbol': symbol, 'token': API_KEY}
        data = make_api_request(QUOTE_ENDPOINT, params)
        
        volume = data.get('v')  # 'v' is Finnhub's volume field
        
        if volume is None:
            logger.warning(f"No volume data for {symbol}")
            return None
        
        if not isinstance(volume, (int, float)) or volume < 0:
            raise DataValidationError(f"Invalid volume data for {symbol}: {volume}")
        
        logger.debug(f"{symbol} current volume: {volume:,.0f}")
        return float(volume)
        
    except FinnhubAPIError as e:
        logger.error(f"API error fetching volume for {symbol}: {e}")
        return None
    except DataValidationError as e:
        logger.error(f"Data validation error for {symbol}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching volume for {symbol}: {e}")
        return None

def get_average_volume(symbol: str, days: int = 20) -> Optional[float]:
    """
    Fetch 20-day average volume using quote data
    NOTE: Finnhub quote endpoint doesn't include historical avg volume directly.
    This uses 'vw' (volume weighted average price) as proxy or requires additional data call.
    For production, consider using historical endpoint or caching daily volumes.
    
    Args:
        symbol: Stock ticker symbol
        days: Number of days for average (default 20)
        
    Returns:
        Average volume as float, or None if error
    """
    try:
        if not API_KEY or API_KEY == "YOUR_FINNHUB_API_KEY":
            return None
        
        params = {'symbol': symbol, 'token': API_KEY}
        data = make_api_request(QUOTE_ENDPOINT, params)
        
        # Get current volume as baseline
        current_vol = data.get('v')
        
        # For a more accurate 20-day average, you would need to call the candles endpoint
        # and average the volumes. This is a simplified version that estimates based on
        # the assumption that today's volume is roughly average (conservative estimate)
        
        if current_vol is None:
            logger.warning(f"No volume data available for {symbol} average")
            return None
        
        # RECOMMENDED: Use candles endpoint for real 20-day average
        avg_volume = get_20day_average_from_candles(symbol)
        
        if avg_volume:
            logger.debug(f"{symbol} 20-day average volume: {avg_volume:,.0f}")
            return avg_volume
        else:
            logger.warning(f"Could not calculate 20-day average for {symbol}, using current as estimate")
            return current_vol * 0.9  # Conservative estimate
        
    except Exception as e:
        logger.error(f"Error calculating average volume for {symbol}: {e}")
        return None

def get_20day_average_from_candles(symbol: str, days: int = 20) -> Optional[float]:
    """
    Fetch 20-day average volume using candles (OHLCV) data
    
    Args:
        symbol: Stock ticker symbol
        days: Number of days to average
        
    Returns:
        Average volume, or None if error
    """
    try:
        if not API_KEY or API_KEY == "YOUR_FINNHUB_API_KEY":
            return None
        
        # Get yesterday's date for data pull
        to_date = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        params = {
            'symbol': symbol,
            'from': from_date,
            'to': to_date,
            'token': API_KEY
        }
        
        candles_url = f"{FINNHUB_BASE_URL}/stock/candle"
        data = make_api_request(candles_url, params)
        
        if not data.get('v'):  # 'v' array contains volumes
            logger.warning(f"No candle data for {symbol}")
            return None
        
        volumes = data['v']
        if not volumes:
            return None
        
        # Calculate average, excluding outliers (optional)
        avg = sum(volumes) / len(volumes)
        logger.debug(f"{symbol} calculated 20-day avg from {len(volumes)} candles: {avg:,.0f}")
        return avg
        
    except FinnhubAPIError as e:
        logger.error(f"API error fetching candles for {symbol}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error processing candles for {symbol}: {e}")
        return None

def check_for_news(symbol: str) -> bool:
    """
    Fetch recent news and check for catalyst keywords
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        True if catalyst news found, False otherwise
    """
    try:
        if not API_KEY or API_KEY == "YOUR_FINNHUB_API_KEY":
            return False
        
        # Get news from last 7 days
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        to_date = datetime.now().strftime('%Y-%m-%d')
        
        params = {
            'symbol': symbol,
            'from': from_date,
            'to': to_date,
            'token': API_KEY
        }
        
        data = make_api_request(NEWS_ENDPOINT, params)
        
        if not data:
            logger.debug(f"No news found for {symbol}")
            return False
        
        news_items = data if isinstance(data, list) else data.get('news', [])
        
        for news in news_items[:10]:  # Check top 10 recent articles
            headline = news.get('headline', '').lower()
            summary = news.get('summary', '').lower()
            
            # Check if any catalyst keyword is in headline or summary
            for keyword in CATALYST_KEYWORDS:
                if keyword.lower() in headline or keyword.lower() in summary:
                    logger.info(f"CATALYST DETECTED for {symbol}: {news.get('headline')}")
                    return True
        
        logger.debug(f"No catalyst keywords found in {symbol} news")
        return False
        
    except FinnhubAPIError as e:
        logger.error(f"API error fetching news for {symbol}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking news for {symbol}: {e}")
        return False

# --- MAIN SCANNER ---
def run_scanner():
    """Main scanner loop with error handling and control flow"""
    logger.info("=" * 60)
    logger.info("VOLUME SCANNER INITIALIZED")
    logger.info(f"Watchlist: {', '.join(WATCHLIST)}")
    logger.info(f"RVOL Threshold: {RVOL_THRESHOLD}x")
    logger.info(f"Scan Interval: {SCAN_INTERVAL}s")
    logger.info(f"Control File: {CONTROL_FILE}")
    logger.info("=" * 60)
    
    daily_picks = load_previous_alerts()
    session_start = datetime.now()
    scan_count = 0
    
    try:
        while True:
            # Check control file
            if not control_file_exists():
                logger.info(f"Control file not found. Waiting for {CONTROL_FILE}...")
                time.sleep(10)
                continue
            
            # Check market hours
            if not is_market_hours():
                current_time = datetime.now(PST).strftime('%H:%M:%S PST')
                logger.debug(f"Outside market hours ({current_time}). Skipping scan.")
                time.sleep(SCAN_INTERVAL)
                continue
            
            scan_count += 1
            logger.info(f"\n--- SCAN #{scan_count} at {datetime.now().strftime('%H:%M:%S')} ---")
            
            alert_found = False
            
            for symbol in WATCHLIST:
                try:
                    # Fetch data with error handling
                    curr_vol = get_current_volume(symbol)
                    avg_vol = get_average_volume(symbol)
                    
                    # Validate data before calculation
                    if curr_vol is None or avg_vol is None:
                        logger.warning(f"Skipping {symbol}: insufficient data")
                        continue
                    
                    if avg_vol == 0:
                        logger.warning(f"Skipping {symbol}: avg volume is zero")
                        continue
                    
                    # Calculate RVOL
                    rvol = curr_vol / avg_vol
                    logger.info(f"{symbol} | RVOL: {rvol:.2f}x | {curr_vol:,.0f} / {avg_vol:,.0f}")
                    
                    # Check alert condition
                    if rvol >= RVOL_THRESHOLD:
                        has_news = check_for_news(symbol)
                        
                        if has_news and symbol not in daily_picks:
                            alert_message = f"🚨 ALERT: {symbol} | RVOL: {rvol:.2f}x + CATALYST NEWS"
                            logger.warning(alert_message)
                            print(f"\n{alert_message}\n")
                            daily_picks.add(symbol)
                            save_alert(symbol)
                            alert_found = True
                        elif has_news:
                            logger.info(f"{symbol} already alerted today (cached)")
                
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
                    continue
            
            if not alert_found:
                logger.info("No new alerts this scan.")
            
            logger.info(f"Next scan in {SCAN_INTERVAL}s...")
            time.sleep(SCAN_INTERVAL)
    
    except KeyboardInterrupt:
        logger.info("\nScanner stopped by user.")
    except Exception as e:
        logger.critical(f"Critical error in main loop: {e}", exc_info=True)
        raise

# --- STARTUP/CONTROL ---
def create_control_file():
    """Create control file to start scanner"""
    try:
        with open(CONTROL_FILE, 'w') as f:
            f.write(f"Scanner control file created at {datetime.now()}\n")
        logger.info(f"Control file created: {CONTROL_FILE}")
    except Exception as e:
        logger.error(f"Could not create control file: {e}")

def delete_control_file():
    """Delete control file to stop scanner"""
    try:
        if os.path.exists(CONTROL_FILE):
            os.remove(CONTROL_FILE)
            logger.info(f"Control file removed: {CONTROL_FILE}")
    except Exception as e:
        logger.error(f"Could not remove control file: {e}")

if __name__ == "__main__":
    logger.info(f"API Key configured: {bool(API_KEY and API_KEY != 'YOUR_FINNHUB_API_KEY')}")
    
    # Uncomment to create control file on startup
    # create_control_file()
    
    # Start the scanner
    run_scanner()
