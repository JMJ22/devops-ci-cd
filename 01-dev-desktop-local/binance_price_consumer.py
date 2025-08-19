import websocket
import json
import threading
import time
import sys
from rich.live import Live
from rich.table import Table
from datetime import datetime

# INTEGRAÇÃO FLASK
from flask import Flask, jsonify
from flask_cors import CORS  # <-- ADICIONE ESTA LINHA
import os

PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
prices = {pair: "-" for pair in PAIRS}
opens = {pair: "-" for pair in PAIRS}
percents = {pair: "-" for pair in PAIRS}
percent_colors = {pair: "white" for pair in PAIRS}
times = {pair: "-" for pair in PAIRS}

running = True

def make_table():
    table = Table(title="Cotações em Tempo Real (Binance) - Use Ctrl+C para sair")
    table.add_column("Par", style="bold cyan")
    table.add_column("Abertura do Dia", style="yellow", justify="right")
    table.add_column("Preço", style="bold green", justify="right")
    table.add_column("Variação (%)", justify="right")
    table.add_column("Atualizado em", style="bold magenta")
    for pair in PAIRS:
        percent_val = percents[pair]
        percent_color = percent_colors[pair]
        percent_styled = f"[{percent_color}]{percent_val}[/{percent_color}]" if percent_val != "-" else "-"
        table.add_row(
            pair,
            str(opens[pair]),
            str(prices[pair]),
            percent_styled,
            str(times[pair])
        )
    return table

def on_message(ws, message):
    data = json.loads(message)
    symbol = data.get('s')
    price = data.get('c')
    open_price = data.get('o')
    if symbol in PAIRS and price:
        prices[symbol] = f"{float(price):,.2f}"
        times[symbol] = datetime.now().strftime('%H:%M:%S')
        if open_price:
            opens[symbol] = f"{float(open_price):,.2f}"
            try:
                pct = ((float(price) - float(open_price)) / float(open_price)) * 100
                percents[symbol] = f"{pct:+.2f}%"
                if pct > 0:
                    percent_colors[symbol] = "bright_green"
                elif pct < 0:
                    percent_colors[symbol] = "red"
                else:
                    percent_colors[symbol] = "white"
            except Exception:
                percents[symbol] = "-"
                percent_colors[symbol] = "white"
        else:
            percents[symbol] = "-"
            percent_colors[symbol] = "white"

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

# FLASK SERVER PARA INTEGRAÇÃO
app = Flask(__name__)
CORS(app)  # <-- ADICIONE ESTA LINHA

@app.route("/cotacoes")
def cotacoes():
    return jsonify({
        "pairs": PAIRS,
        "prices": prices,
        "opens": opens,
        "percents": percents,
        "percent_colors": percent_colors,
        "times": times,
    })

def flask_server():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    t = threading.Thread(target=run_ws, daemon=True)
    t.start()
    # Inicia o Flask em uma thread separada
    flask_thread = threading.Thread(target=flask_server, daemon=True)
    flask_thread.start()
    try:
        with Live(make_table(), refresh_per_second=4) as live:
            while True:
                live.update(make_table())
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nFinalizado.")
        sys.exit(0)
