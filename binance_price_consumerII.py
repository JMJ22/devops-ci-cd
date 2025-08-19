import websocket
import json
import threading
import time
from datetime import datetime
from collections import defaultdict
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
import plotext as plt

PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
prices = {pair: "-" for pair in PAIRS}
times = {pair: "-" for pair in PAIRS}

ohlc_by_minute = defaultdict(lambda: [None, None, None, None])
ohlc_minutes = []

def make_table():
    table = Table(title="Cotações em Tempo Real (Binance)")
    table.add_column("Par", style="bold cyan")
    table.add_column("Preço", style="bold green", justify="right")
    table.add_column("Atualizado em", style="bold magenta")
    for pair in PAIRS:
        table.add_row(pair, str(prices[pair]), str(times[pair]))
    return table

def make_candlestick():
    N = 15
    candles = []
    for i, minute in enumerate(ohlc_minutes[-N:]):
        o, h, l, c = ohlc_by_minute[minute]
        if None not in (o, h, l, c):
            candles.append([i, o, h, l, c])
    if len(candles) >= 2:
        plt.clear_data()
        x = [item[0] for item in candles]
        data = [item[1:] for item in candles]
        plt.candlestick(x, data)
        plt.title("BTCUSDT - Candlestick (1min)")
        plt.canvas_color('black')
        plt.axes_color('black')
        plt.ticks_color('white')
        plt.xlabel("Minuto")
        plt.ylabel("USDT")
        # Gera o gráfico como string (ASCII) para Rich
        chart_str = plt.build()
        return chart_str
    return "Aguardando dados suficientes para o gráfico..."

def make_layout():
    table = make_table()
    chart = make_candlestick()
    # Junte tabela Rich e gráfico plotext em um Panel
    return Panel(f"{table}\n\n{chart}", border_style="magenta")

def on_message(ws, message):
    data = json.loads(message)
    symbol = data.get('s')
    price = data.get('c')
    if symbol in PAIRS and price:
        price = float(price)
        prices[symbol] = f"{price:,.2f}"
        times[symbol] = datetime.now().strftime('%H:%M:%S')
        # Agrupar ticks por minuto para BTCUSDT
        if symbol == "BTCUSDT":
            now = datetime.now()
            minute_str = now.strftime("%Y-%m-%d %H:%M")
            ohlc = ohlc_by_minute[minute_str]
            if ohlc[0] is None:  # open
                ohlc[0] = price
                ohlc[1] = price  # high
                ohlc[2] = price  # low
                ohlc[3] = price  # close
                ohlc_minutes.append(minute_str)
            else:
                ohlc[1] = max(ohlc[1], price)  # high
                ohlc[2] = min(ohlc[2], price)  # low
                ohlc[3] = price                # close

def on_error(ws, error):
    print(f"Erro: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket fechado")

def on_open(ws):
    params = [f"{pair.lower()}@ticker" for pair in PAIRS]
    ws.send(json.dumps({
        "method": "SUBSCRIBE",
        "params": params,
        "id": 1
    }))

def run_ws():
    ws_url = "wss://stream.binance.com:9443/ws"
    ws = websocket.WebSocketApp(ws_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()

if __name__ == "__main__":
    print("Iniciando consumidor Binance...")
    t = threading.Thread(target=run_ws, daemon=True)
    t.start()
    time.sleep(2)
    with Live(make_layout(), refresh_per_second=4) as live:
        while True:
            live.update(make_layout())
            time.sleep(1)
