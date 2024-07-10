from flask import Flask, jsonify
import asyncio
from binance_trading.binanceSocket import start_websocket_client
from binance_trading.binance_api import get_candles
from binance_trading.trading_strategy import TradingStrategy

app = Flask(__name__)
trading_strategy = TradingStrategy()

@app.route('/')
def index():
    return "API corriendo satisfactoriamente"

@app.route('/start_websocket')
def start_websocket():
    # Iniciar el cliente WebSocket en un hilo separado para no bloquear la aplicación Flask
    asyncio.run(start_websocket_client())
    return "Cliente WebSocket iniciado"

@app.route('/velas')
async def get_historical_futures_klines_api():
    klines = await get_candles()
    return jsonify(klines)

@app.route('/process_data', methods=['POST'])
def process_data():
    data = request.json
    trading_strategy.process_real_time_data(data)
    return "Datos procesados"

if __name__ == "__main__":
    app.run(port=3030)