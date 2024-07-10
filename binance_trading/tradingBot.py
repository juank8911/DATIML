from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import time
import binance_api

class TradingBot:
    """A class representing a trading bot that predicts and executes trades on Binance."""

    def __init__(self, symbol, interval, start_time):
        """Initialize the TradingBot with symbol, interval, start time, balance, fees, model, and opened trades."""
        self.symbol = symbol
        self.interval = interval
        self.start_time = start_time
        self.balance = 100  # Initial balance in USDT
        self.fee = binance_api.get_fees()  # Binance fees
        self.model = None
        self.opened_trades = []  # List of open trades

    def train_model(self, X, y):
        """Train the Random Forest model, evaluate it, and start the observation and trading loop."""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = model.score(X_test, y_test)
        print("Accuracy:", accuracy)
        self.model = model
        self.observe_and_trade()

    def observe_and_trade(self):
        """Constantly observe the data, predict trades, and execute trading decisions."""
        while True:
            klines = binance_api.get_historical_futures_klines()
            trades = self.predict_trades(klines)
            for trade in trades:
                self.execute_trade(trade)
            time.sleep(5)

    def predict_trades(self, klines):
        """Process data, predict trades using the ML model, and return the predicted trades."""
        df = pd.DataFrame(klines)
        trades = self.model.predict(df)
        return trades

    def execute_trade(self, trade):
        """Open or close trades on Binance based on the prediction."""
        if trade == 1:  # Long
            self.open_long_trade()
        elif trade == -1:  # Short
            self.open_short_trade()
        elif trade == 0:  # Close long
            self.close_long_trade()
        elif trade == 2:  # Close short
            self.close_short_trade()

    def open_long_trade(self):
        """Open a long trade on Binance with leverage."""
        value_to_invest = self.calculate_value_to_invest()
        max_leverage = binance_api.get_maximum_leverage(self.symbol)
        leverage = min(70 * max_leverage // 100, max_leverage)
        order = binance_api.open_long_trade_with_leverage(self.symbol, value_to_invest, leverage)
        self.execute_transactions(order)
        self.save_earn_flexible()
        self.opened_trades.append(order)

    def close_long_trade(self):
        """Close a long trade on Binance."""
        value_to_invest = self.calculate_value_to_invest()
        order = binance_api.close_long_trade(self.symbol, value_to_invest)
        self.execute_transactions(order)
        self.save_earn_flexible()
        self.opened_trades.remove(order)

    def open_short_trade(self):
        """Open a short trade on Binance with leverage."""
        value_to_invest = self.calculate_value_to_invest()
        max_leverage = binance_api.get_maximum_leverage(self.symbol)
        leverage = min(70 * max_leverage // 100, max_leverage)
        order = binance_api.open_short_trade_with_leverage(self.symbol, value_to_invest, leverage)
        self.execute_transactions(order)
        self.opened_trades.append(order)

    def close_short_trade(self):
        """Close a short trade on Binance."""
        value_to_invest = self.calculate_value_to_invest()
        order = binance_api.close_short_trade(self.symbol, value_to_invest)
        self.execute_transactions(order)
        self.opened_trades.remove(order)

    def calculate_value_to_invest(self):
        """Calculate the value to invest based on the current balance."""
        if self.balance <= 1.5:
            return self.balance * 0.9
        elif self.balance <= 3:
            return (self.balance - 1.5) * 0.9
        elif self.balance <= 9:
            return (self.balance - 3) * 0.9
        else:
            return (self.balance - 9) * 0.9

    def execute_transactions(self, order):
        """Execute transactions with leverage on Binance."""
        value_to_trade = order['value'] * 0.7
        binance_api.execute_trade(self.symbol, value_to_trade, order['type'])

    def save_earn_flexible(self):
        """Save 25% of the gain in earn flexible."""
        gain = self.balance * 0.25
        binance_api.save_earn_flexible(self.symbol, gain)
        
        
        