# hybrid-ai-trading-assistant-backend/derived_api.py
import asyncio
import websockets
import json
import os
from ratelimit import limits, RateLimitException, sleep_and_retry

# --- Deriv API Endpoint ---
DERIV_WEBSOCKET_URL = "wss://ws.binaryws.com/websockets/v3"

# --- API Credentials and Rate Limits (HARDCODED DEFAULTS - MUST BE REPLACED) ---
API_KEY = os.getenv("DERIVED_API_KEY", "YOUR_DEFAULT_API_KEY")  # Default, MUST be overridden
APP_ID = os.getenv("DERIVED_APP_ID", "YOUR_DEFAULT_APP_ID")    # Default, MUST be overridden
CALLS_PER_MINUTE = int(os.getenv("CALLS_PER_MINUTE", 60))       # Default, can be overridden
CALLS_PER_SECOND = int(os.getenv("CALLS_PER_SECOND", 1))        # Default, can be overridden


# --- Rate Limiting Decorators ---
@sleep_and_retry
@limits(calls=CALLS_PER_MINUTE, period=60)
async def call_api_per_minute(websocket, request):
    await websocket.send(request)
    response = await websocket.recv()
    return response

@sleep_and_retry
@limits(calls=CALLS_PER_SECOND, period=1)
async def call_api_per_second(websocket, request):
    await websocket.send(request)
    response = await websocket.recv()
    return response

# --- API Interaction Functions ---

async def get_rate_limits():
    """Fetches API call limits from Deriv (updates globals)."""
    global CALLS_PER_MINUTE, CALLS_PER_SECOND
    if not API_KEY or not APP_ID:
        print("WARNING: API_KEY or APP_ID not set.  Using default rate limits.")
        return  # Use defaults if not set

    uri = f"{DERIV_WEBSOCKET_URL}?app_id={APP_ID}"
    try:
        async with websockets.connect(uri) as websocket:
            request = json.dumps({"website_status": 1})
            await call_api_per_second(websocket, request)
            response = await call_api_per_second(websocket, request)
            response_data = json.loads(response)
            if 'website_status' in response_data and 'api_call_limits' in response_data['website_status']:
                limits = response_data['website_status']['api_call_limits']
                CALLS_PER_MINUTE = int(limits.get('calls_per_minute', CALLS_PER_MINUTE))
                CALLS_PER_SECOND = int(limits.get('max_calls_per_second', CALLS_PER_SECOND))
                print(f"Fetched API Rate Limits: Per Minute={CALLS_PER_MINUTE}, Per Second={CALLS_PER_SECOND}")
            else:
                print("Could not retrieve API rate limits. Using defaults.")
    except (websockets.exceptions.ConnectionClosedError, Exception, RateLimitException) as e:
        print(f"Error fetching rate limits: {e}. Using defaults.")
    return  # No need to return, globals are updated

async def get_historical_digits(symbol="R_100", count=1000, end="latest", start=1):
    """Fetches historical digit data from Deriv."""
    if not API_KEY or not APP_ID:
        raise ValueError("API_KEY and APP_ID must be set.")
    uri = f"{DERIV_WEBSOCKET_URL}?app_id={APP_ID}"
    try:
        async with websockets.connect(uri) as websocket:
            auth_request = json.dumps({"authorize": API_KEY})
            await call_api_per_minute(websocket, auth_request)
            ticks_request = json.dumps({
                "ticks_history": symbol, "start": start, "end": end, "style": "ticks", "count": count
            })
            await call_api_per_second(websocket, ticks_request)
            ticks_response = await call_api_per_second(websocket, ticks_request)
            ticks_data = json.loads(ticks_response)
            if 'history' in ticks_data and 'prices' in ticks_data['history']:
                return [int(str(price)[-1]) for price in ticks_data['history']['prices'] if isinstance(price,(str,int,float))]
            else:
                print(f"Unexpected API response: {ticks_data}")
                return []
    except (websockets.exceptions.ConnectionClosedError, Exception, RateLimitException) as e:
        print(f"Error fetching historical data: {e}")
        return []

async def subscribe_to_ticks(symbol="R_100"):
    """Subscribes to real-time tick stream for a symbol."""
    if not API_KEY or not APP_ID:
        raise ValueError("API_KEY and APP_ID must be set.")
    uri = f"{DERIV_WEBSOCKET_URL}?app_id={APP_ID}"
    reconnect_delay = 5
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                auth_request = json.dumps({"authorize": API_KEY})
                await call_api_per_minute(websocket, auth_request)
                subscribe_request = json.dumps({"ticks": symbol, "subscribe": 1})
                await call_api_per_second(websocket, subscribe_request)
                print(f"Subscribed to tick stream for {symbol}")
                while True:
                    response = await call_api_per_second(websocket,'')
                    tick_data = json.loads(response)
                    if 'tick' in tick_data and 'quote' in tick_data['tick']:
                        yield int(str(tick_data['tick']['quote'])[-1])
                    elif 'error' in tick_data:
                        print(f"Error in stream: {tick_data['error']}")
                        break
            reconnect_delay = 5

        except (websockets.exceptions.ConnectionClosedError, Exception, RateLimitException) as e:
            print(f"Error in subscribe_to_ticks: {e}, reconnecting in {reconnect_delay}s")
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 60)

async def place_trade(trade_params):
    """Placeholder for placing a trade."""
    print("PLACEHOLDER: Placing trade...")
    pass

async def cancel_trade(trade_id):
    """Placeholder for canceling a trade."""
    print("PLACEHOLDER: Canceling trade...")
    pass
