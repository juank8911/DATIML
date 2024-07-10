from flask import Flask, jsonify
import ccxt
import os
import logging
import time
import asyncio
import websockets
from binance_trading.binance_api import receive_socket_data

app = Flask(__name__)
app.run(port=3030)


@app.route('/')
def index():
    asyncio.get_event_loop().run_until_complete(receive_socket_data())
    return "API corrida satisfactoriamente"
    


@app.route('/velas')
async def get_historical_futures_klines_api():
    asyncio.get_event_loop().run_until_complete(receive_socket_data())
#     symbols = await get_exchange_info()
#     print(symbols)
#     klines = await get_candles(symbols)
#     return jsonify(klines)

async def listen_ws():
    uri = "ws://localhost:3000/ws"  # Update the URI with your server address
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello, WebSocket server!")
        response = await websocket.recv()
        print(f"Received message from server: {response}")


if __name__ == "__main__":
    app.run()
    asyncio.get_event_loop().run_until_complete(listen_ws())
    