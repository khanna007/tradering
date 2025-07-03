import MetaTrader5 as mt5
import time
from datetime import datetime

# === Strategy Configuration ===
SYMBOL = "XAUUSD"
TIMEFRAME = mt5.TIMEFRAME_M1
INITIAL_CAPITAL = 20.0
RISK_PER_TRADE = 0.01
TP_PIPS = 10
SL_PIPS = 5
MAX_TRADES_PER_DAY = 100
DAILY_TARGET_RETURN = 0.195
bot_running = True

# === Helper Functions ===
def initialize():
    if not mt5.initialize():
        print("MT5 initialization failed:", mt5.last_error())
        quit()

def get_data(symbol, timeframe, bars=200):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    return rates

def calculate_ema(prices, span):
    ema = []
    k = 2 / (span + 1)
    ema.append(prices[0])
    for price in prices[1:]:
        ema.append((price * k) + (ema[-1] * (1 - k)))
    return ema

def calculate_rsi(prices, period=14):
    gains = []
    losses = []
    for i in range(1, period + 1):
        delta = prices[i] - prices[i - 1]
        if delta > 0:
            gains.append(delta)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(delta))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def generate_signal(data):
    closes = [bar['close'] for bar in data]
    if len(closes) < 200:
        return None
    ema50 = calculate_ema(closes, 50)
    ema200 = calculate_ema(closes, 200)
    rsi = calculate_rsi(closes[-15:])  # last 15 closes
    if ema50[-1] > ema200[-1] and rsi < 45:
        return "buy"
    elif ema50[-1] < ema200[-1] and rsi > 55:
        return "sell"
    return None

def get_lot_size(balance):
    return round(balance * RISK_PER_TRADE / 100, 2)

def has_open_positions(symbol):
    positions = mt5.positions_get(symbol=symbol)
    return positions is not None and len(positions) > 0

def send_order(symbol, action, lot):
    tick = mt5.symbol_info_tick(symbol)
    price = tick.ask if action == "buy" else tick.bid
    deviation = 20
    sl = price - SL_PIPS * 0.1 if action == "buy" else price + SL_PIPS * 0.1
    tp = price + TP_PIPS * 0.1 if action == "buy" else price - TP_PIPS * 0.1

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY if action == "buy" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": 10032025,
        "comment": "XAU Scalping Bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    print("Trade result:", result)

def run_strategy():
    initialize()
    day_trade_count = 0
    account_info = mt5.account_info()
    if account_info is None:
        print("Failed to get account info")
        return
    start_equity = account_info.equity
    target_equity = start_equity * (1 + DAILY_TARGET_RETURN)

    while bot_running and day_trade_count < MAX_TRADES_PER_DAY:
        data = get_data(SYMBOL, TIMEFRAME)
        if data is None or len(data) < 200:
            time.sleep(60)
            continue

        signal = generate_signal(data)
        if signal and not has_open_positions(SYMBOL):
            balance = mt5.account_info().balance
            lot = get_lot_size(balance)
            send_order(SYMBOL, signal, lot)
            day_trade_count += 1

        if mt5.account_info().equity >= target_equity:
            print("Daily target reached.")
            break

        time.sleep(60)

    mt5.shutdown()

if __name__ == "__main__":
    run_strategy()
