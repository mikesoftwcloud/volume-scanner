#!/usr/bin/env python3
"""
Test script to validate Finnhub API setup and data quality
Run this before starting the main scanner
"""

import os
import requests
import logging
from datetime import datetime, timedelta
import pytz

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load from environment
API_KEY = os.getenv("FINNHUB_API_KEY")
TEST_SYMBOLS = ["NOK", "AAPL", "TSLA"]
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

def test_api_connection():
    """Test basic API connectivity"""
    logger.info("=" * 60)
    logger.info("TEST 1: API Connection")
    logger.info("=" * 60)
    
    if not API_KEY:
        logger.error("❌ FINNHUB_API_KEY not set in environment")
        logger.info("   Set it: export FINNHUB_API_KEY='your_key_here'")
        return False
    
    logger.info(f"✓ API Key found: {API_KEY[:10]}...")
    
    try:
        response = requests.get(
            f"{FINNHUB_BASE_URL}/quote",
            params={"symbol": "AAPL", "token": API_KEY},
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("✓ API endpoint reachable")
            return True
        elif response.status_code == 401:
            logger.error("❌ Invalid API key (401 Unauthorized)")
            return False
        elif response.status_code == 429:
            logger.error("❌ Rate limited (429). Wait a moment and retry.")
            return False
        else:
            logger.error(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("❌ Request timeout. Check internet connection.")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("❌ Connection error. Check internet connection.")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

def test_quote_data():
    """Test fetching quote data"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Quote Data Quality")
    logger.info("=" * 60)
    
    all_passed = True
    
    for symbol in TEST_SYMBOLS:
        try:
            response = requests.get(
                f"{FINNHUB_BASE_URL}/quote",
                params={"symbol": symbol, "token": API_KEY},
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"❌ {symbol}: Status code {response.status_code}")
                all_passed = False
                continue
            
            data = response.json()
            
            # Check required fields
            required_fields = ['c', 'v', 'o', 'h', 'l']  # close, volume, open, high, low
            missing = [f for f in required_fields if f not in data or data[f] is None]
            
            if missing:
                logger.error(f"❌ {symbol}: Missing fields {missing}")
                all_passed = False
                continue
            
            logger.info(f"✓ {symbol} | Price: ${data['c']:.2f} | Volume: {data['v']:,.0f}")
            
        except Exception as e:
            logger.error(f"❌ {symbol}: {e}")
            all_passed = False
    
    return all_passed

def test_news_data():
    """Test fetching news data"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: News Data Quality")
    logger.info("=" * 60)
    
    all_passed = True
    
    for symbol in TEST_SYMBOLS:
        try:
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            response = requests.get(
                f"{FINNHUB_BASE_URL}/company-news",
                params={
                    "symbol": symbol,
                    "from": from_date,
                    "to": to_date,
                    "token": API_KEY
                },
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"❌ {symbol}: Status code {response.status_code}")
                all_passed = False
                continue
            
            data = response.json()
            
            if isinstance(data, list):
                news_count = len(data)
            else:
                news_count = len(data.get('news', []))
            
            if news_count == 0:
                logger.warning(f"⚠ {symbol}: No news found (may be normal)")
            else:
                logger.info(f"✓ {symbol}: {news_count} news articles found")
            
        except Exception as e:
            logger.error(f"❌ {symbol}: {e}")
            all_passed = False
    
    return all_passed

def test_market_hours():
    """Test market hours logic"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Market Hours Detection")
    logger.info("=" * 60)
    
    try:
        PST = pytz.timezone('America/Los_Angeles')
        current_time = datetime.now(PST)
        market_open = current_time.replace(hour=4, minute=0, second=0, microsecond=0)
        market_close = current_time.replace(hour=9, minute=0, second=0, microsecond=0)
        is_open = market_open <= current_time <= market_close
        
        logger.info(f"Current time (PST): {current_time.strftime('%H:%M:%S')}")
        logger.info(f"Market hours: 4:00 AM - 9:00 AM PST")
        logger.info(f"Status: {'✓ OPEN' if is_open else '✗ CLOSED'} (Scanner will {'run' if is_open else 'wait'})")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error checking market hours: {e}")
        return False

def test_candles_data():
    """Test fetching candle/OHLCV data for average volume calculation"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Candle Data (for 20-day avg volume)")
    logger.info("=" * 60)
    
    symbol = "AAPL"
    try:
        to_date = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d')
        
        response = requests.get(
            f"{FINNHUB_BASE_URL}/stock/candle",
            params={
                "symbol": symbol,
                "from": from_date,
                "to": to_date,
                "token": API_KEY
            },
            timeout=10
        )
        
        if response.status_code != 200:
            logger.error(f"❌ Status code {response.status_code}")
            return False
        
        data = response.json()
        
        if 'v' not in data or not data['v']:
            logger.error(f"❌ No volume data in candles")
            return False
        
        volumes = data['v']
        avg_vol = sum(volumes) / len(volumes)
        
        logger.info(f"✓ {symbol}: {len(volumes)} days of candle data")
        logger.info(f"  Average volume: {avg_vol:,.0f}")
        logger.info(f"  Range: {min(volumes):,.0f} - {max(volumes):,.0f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ {symbol}: {e}")
        return False

def test_file_controls():
    """Test file-based control mechanism"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 6: File Control System")
    logger.info("=" * 60)
    
    control_file = "scanner_control.txt"
    
    try:
        # Create control file
        with open(control_file, 'w') as f:
            f.write("test")
        logger.info(f"✓ Created {control_file}")
        
        # Check if it exists
        if os.path.exists(control_file):
            logger.info(f"✓ File control mechanism works")
        
        # Clean up
        os.remove(control_file)
        logger.info(f"✓ Cleaned up test file")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ File control test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    results = {
        "API Connection": test_api_connection(),
        "Quote Data": test_quote_data(),
        "News Data": test_news_data(),
        "Market Hours": test_market_hours(),
        "Candle Data": test_candles_data(),
        "File Controls": test_file_controls(),
    }
    
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        logger.info("\n✓ ALL TESTS PASSED - Ready to run scanner!")
        logger.info("\nNext steps:")
        logger.info("1. Copy .env.example to .env")
        logger.info("2. Add your Finnhub API key to .env")
        logger.info("3. Run: python volume_scanner.py")
        logger.info("4. Create scanner_control.txt to start scanning")
    else:
        logger.error("\n❌ SOME TESTS FAILED - Fix issues before running scanner")
        logger.info("Check logs above for details")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
