import os
import aiohttp
from dotenv import load_dotenv
import websockets

load_dotenv()

binance_api_url = os.getenv('BINANCE_API_URL')

# async def get_exchange_info():
#     """
#     """
#     Fetches exchange information from Binance.

#     Args:
#         client (ccxt.Exchange): The Binance exchange instance.

#     Returns:
#         dict: The exchange information data.
#     """



async def receive_socket_data():
  uri = "ws://localhost:3000/start-socket"  # Replace with the WebSocket server address
  async with websockets.connect(uri) as websocket:
    while True:
      try:
        message = await websocket.recv()
        print('Received data:', message)
        # Process the received data as needed
      except websockets.ConnectionClosed:
        print('Connection closed. Reconnecting...')
        break
      except Exception as e:
        print('Error receiving data:', e)
        # Handle errors appropriately (e.g., retry connection)


async def get_candles():
    """
    Fetches candles for all perpetual futures with USDT/USDC pairs on Binance futures.

    Returns:
        list: List of dictionaries with symbol information and candles data.
    """
    url = f"{binance_api_url}/bin/velas"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    symbols = []
    for symbol in data:
        symbol_info = symbol["symbol"]
        candles = symbol["data"]
        symbol_info["candles"] = candles
        symbols.append(symbol_info)
    return symbols
    

async def abrir_operacion_futuros_apalancada(exchange, simbolo, apalancamiento, cantidad,lado, tipo_orden="mercado" ):
  """
  Esta función abre una operación de futuros apalancada (corta o larga) en el exchange especificado.

  Args:
      exchange (ccxt.Exchange): Instancia del exchange CCXT configurada con sus credenciales.
      simbolo (str): Símbolo del contrato de futuros (ej.: BTC/USDT).
      apalancamiento (int): Nivel de apalancamiento deseado.
      cantidad (float): Cantidad del activo subyacente a operar (considerando el apalancamiento).
      tipo_orden (str, opcional): Tipo de orden ("mercado" o "limite"). Predeterminado a "mercado".
      lado (str, opcional): Dirección de la operación ("corto" o "largo"). Predeterminado a "corto".

  Returns:
      dict: Diccionario con la información de la orden creada.
  """
  
