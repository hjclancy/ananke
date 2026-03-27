import anthropic
import json

client = anthropic.Anthropic()

# --- Robinhood tool functions ---

def get_portfolio():
    positions = rh.get_open_stock_positions()
    holdings = []
    for p in positions:
        instrument = rh.get_instrument_by_url(p['instrument'])
        holdings.append({
            "symbol": instrument['symbol'],
            "quantity": p['quantity'],
            "avg_cost": p['average_buy_price'],
        })
    return holdings

def get_quote(symbol: str):
    return rh.get_latest_price(symbol)

def get_account_info():
    profile = rh.load_portfolio_profile()
    return {
        "equity": profile['equity'],
        "cash": profile['withdrawable_amount'],
        "buying_power": profile['buying_power'],
    }

def place_market_order(symbol: str, quantity: float, side: str):
    """side = 'buy' or 'sell'"""
    if side == "buy":
        return rh.order_buy_market(symbol, quantity)
    elif side == "sell":
        return rh.order_sell_market(symbol, quantity)

# --- Tool definitions for Claude ---

tools = [
    {
        "name": "get_portfolio",
        "description": "Get all current stock holdings and positions",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "get_quote",
        "description": "Get the latest price for a stock ticker",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Stock ticker, e.g. AAPL"}
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_account_info",
        "description": "Get account equity, cash, and buying power",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "place_market_order",
        "description": "Place a market buy or sell order. ALWAYS confirm with user before calling.",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string"},
                "quantity": {"type": "number"},
                "side": {"type": "string", "enum": ["buy", "sell"]}
            },
            "required": ["symbol", "quantity", "side"]
        }
    }
]
