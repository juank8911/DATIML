import websocket
import json
import asyncio

async def on_message(ws, message):
    data = json.loads(message)
    print(f"Datos recibidos: {data}")
    # Aquí puedes procesar los datos como necesites

async def on_error(ws, error):
    print(f"Error: {error}")

async def on_close(ws, close_status_code, close_msg):
    print("Conexión cerrada")

async def on_open(ws):
    print("Conexión abierta")

async def start_websocket_client():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:3000/binance-stream",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                on_open=on_open)

    wst = asyncio.get_event_loop().run_in_executor(None, ws.run_forever)
    print("WebSocket client iniciado")
    await wst

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_websocket_client())