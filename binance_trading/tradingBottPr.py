import json
import requests
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import websocket
import time
import binance_api

class TradingBottPr:
    
    def __init__(self):
        self.cndles = binance_api.get_candles
    """A class representing a trading bot that predicts and executes trades on Binance."""
    def load_historical_data(self, file_path):
        """Load historical data from a JSON file."""
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data

    def select_promising_tokens(self, data):
        """Select promising tokens based on price fluctuation rules."""
        promising_tokens = []
        candles = self.cndles()
        for symbol in data:
            name = symbol['symbol']['name']
            open_prices = [float(item['open']) for item in candles[name]]
            max_prices = [float(item['high']) for item in candles[name]]
            min_prices = [float(item['low']) for item in candles[name]]
            fluctuation_percentages = []
            for i in range(1, len(open_prices)):
                open_price = open_prices[i]
                max_price = max_prices[i]
                min_price = min_prices[i]
                fluctuation = (open_price - min_price) / min_price * 100
                fluctuation_percentage = fluctuation / max_price * 100
                fluctuation_percentages.append(fluctuation_percentage)
                if len(fluctuation_percentages) >= 20:
                    grouped_fluctuations = [sum(fluctuation_percentages[i:i+3]) / 3 for i in range(0, len(fluctuation_percentages), 3)]
                    if any(grouped_fluctuation > 0.5 for grouped_fluctuation in grouped_fluctuations):
                        promising_tokens.append(name)
                        break
        return promising_tokens
    
    def monitor_webSocket(self, url):
        """Monitor a webSocket and analyze the received data."""
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(url, on_message=self.on_message)
        ws.run_forever()

    def on_message(self, ws, message):
        """Handle incoming messages from the webSocket."""
        data = json.loads(message)
        for token in data:
            if token['s'] in self.promising_tokens:
                self.analyze_token(token)

    def analyze_token(self, token):
        """Analyze a token and predict a trade."""
        fluctuation_30 = abs(token['fluctua'] - 0.005) < 0.005
        fluctuation_60 = abs(token['fluctua'] - 0.01) < 0.01
        fluctuation_90 = abs(token['fluctua'] - 0.015) < 0.015
        if fluctuation_30 and fluctuation_60 and fluctuation_90:
            self.predict_trade(token)

    def predict_trade(self, token):
        """Predict a trade based on price fluctuation."""
        if token['r'] > 0:
            side = 'BUY'
        else:
            side = 'SELL'
        self.execute_trade(token['s'], side)

    def execute_trade(self, symbol, side):
        """Execute a trade."""
        batch_orders = [
            {
                'symbol': symbol,
                'side': side,
                'type': 'LIMIT',
                'quantity': 1,
                'price': 0.001
            }
        ]
        response = requests.post('http://localhost:3000/bina/open', json=batch_orders)
        print(response.json())

    def monitor_open_trades(self):
        """Monitor open trades and close them if profitable."""
        while True:
            open_trades = self.get_open_trades()
            for trade in open_trades:
                profit_percentage = self.calculate_profit_percentage(trade)
                if profit_percentage > 0.05:
                    self.close_trade(trade)
            time.sleep(60)

    def get_open_trades(self):
        """Get open trades from the API."""
        response = requests.get('http://localhost:3000/bina/open')
        return response.json()

    def calculate_profit_percentage(self, trade):
        """Calculate the profit percentage of a trade."""
        profit = trade['profit']
        initial_investment = trade['initial_investment']
        return profit / initial_investment * 100
    
    
    def open_trades(self, tokens):
        """Open multiple trades."""
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

    def close_trade(self, trade):
        """Close a trade."""
        batch_orders = [
            {
                'symbol': trade['symbol'],
                'side': 'SELL' if trade['side'] == 'BUY' else 'BUY',
                'type': 'LIMIT',
                'quantity': 1,
                'price': trade['price']
            }
        ]
        response = requests.post('http://localhost:3000/bina/close', json=batch_orders)
        print(response.json())
        
        
# Para exportar la clase y poder importarla desde otro archivo

all = ['TradingBottPr']
