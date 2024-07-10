from flask import Flask, jsonify
import asyncio
from binance_trading.binanceSocket import start_websocket_client
from binance_trading.binance_api import get_candles,get_exchange_info

app = Flask(__name__)

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
    async def get_historical_futures_klines_api():
        # symbols = await get_exchange_info()
        # print(symbols)
        klines = await get_candles()
        return jsonify(klines)
    return "Función para obtener velas"

if __name__ == "__main__":
    app.run(port=3030)

# @app.route('/')
# def index():
#     asyncio.get_event_loop().run_until_complete(receive_socket_data())
#     return "API corrida satisfactoriamente"
    


# @app.route('/velas')
# async def get_historical_futures_klines_api():
#     asyncio.get_event_loop().run_until_complete(receive_socket_data())
# #     symbols = await get_exchange_info()
# #     print(symbols)
# #     klines = await get_candles(symbols)
# #     return jsonify(klines)
