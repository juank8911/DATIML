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
  
async def getAllOrders():
    url = f"{binance_api_url}/bina/allop"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    return data


async def operar(tokens):
  tokens = tokens
  batch_orders = []
  for token in tokens:
    batch_orders.append({
      'symbol': token['s'],
      'side': 'SELL' if token['side'] == 'BUy' else 'BUY',
      'type': 'LIMIT',
      'quantity': 1,
      'price': token['p']
      })
  response = requests.post('http://localhost:3000/bina/open', json=batch_orders)
  print(response.json())
  
