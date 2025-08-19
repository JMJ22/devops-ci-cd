import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print(data)

def on_open(ws):
    ws.send(json.dumps({
        "method": "SUBSCRIBE",
        "params": ["btcusdt@ticker", "ethusdt@ticker", "bnbusdt@ticker"],
        "id": 1
    }))

ws = websocket.WebSocketApp(
    "wss://stream.binance.com:9443/ws",
    on_open=on_open,
    on_message=on_message
)
ws.run_forever()
