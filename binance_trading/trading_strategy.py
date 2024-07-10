import asyncio
from .TrainingBot import TrainingBot
import joblib
from binance_api import place_order, get_account_balance

class TradingStrategy:
    """
    Clase para implementar la estrategia de trading en tiempo real.
    """

    def __init__(self):
        self.open_positions = {}
        self.model = joblib.load("model.pkl")
        self.bot = TrainingBot

    def process_real_time_data(self, data):
        """
        Procesa los datos en tiempo real y toma decisiones de trading.

        Args:
            data (dict): Datos en tiempo real del símbolo.
        """
        symbol = data['s']
        current_price = float(data['c'])
        
        prediction = self.predict_trades(data)[-1]
        
        if symbol not in self.open_positions:
            if prediction == 1 and self.should_open_long(symbol, current_price):
                self.open_long_position(symbol, current_price)
            elif prediction == 0 and self.should_open_short(symbol, current_price):
                self.open_short_position(symbol, current_price)
        else:
            if self.should_close_position(symbol, current_price):
                self.close_position(symbol, current_price)

    def predict_trades(self, data):
        """
        Utiliza el modelo para predecir operaciones.

        Args:
            data (dict): Datos del símbolo para realizar la predicción.

        Returns:
            np.array: Array de predicciones (0 o 1 para cada punto de datos).
        """
        return self.bot.predict_trades(data)

    def should_open_long(self, symbol, current_price):
        """
        Determina si se debe abrir una posición larga.

        Args:
            symbol (str): Símbolo del par de trading.
            current_price (float): Precio actual del símbolo.

        Returns:
            bool: True si se debe abrir una posición larga, False en caso contrario.
        """
        # Implementa tu lógica aquí, por ejemplo:
        return self.bot.analyzed_data[symbol]['trend'] == 'alcista' and \
               self.bot.analyzed_data[symbol]['upward_count'] > 15

    def should_open_short(self, symbol, current_price):
        """
        Determina si se debe abrir una posición corta.

        Args:
            symbol (str): Símbolo del par de trading.
            current_price (float): Precio actual del símbolo.

        Returns:
            bool: True si se debe abrir una posición corta, False en caso contrario.
        """
        # Implementa tu lógica aquí, por ejemplo:
        return self.bot.analyzed_data[symbol]['trend'] == 'bajista' and \
               self.bot.analyzed_data[symbol]['downward_count'] > 15

    def should_close_position(self, symbol, current_price):
        """
        Determina si se debe cerrar una posición.

        Args:
            symbol (str): Símbolo del par de trading.
            current_price (float): Precio actual del símbolo.

        Returns:
            bool: True si se debe cerrar la posición, False en caso contrario.
        """
        position = self.open_positions[symbol]
        if position['type'] == 'long':
            return current_price <= position['price'] * 0.98 or current_price >= position['price'] * 1.02
        else:
            return current_price >= position['price'] * 1.02 or current_price <= position['price'] * 0.98

    async def open_long_position(self, symbol, price):
        """
        Abre una posición larga.

        Args:
            symbol (str): Símbolo del par de trading.
            price (float): Precio de apertura de la posición.
        """
        print(f"Abriendo posición larga para {symbol} a {price}")
        self.open_positions[symbol] = {'type': 'long', 'price': price}
        
        # Obtener el balance de la cuenta
        balance = await get_account_balance()
        
        # Calcular la cantidad a comprar (por ejemplo, el 1% del balance)
        quantity = (balance * 0.01) / price
        
        # Colocar la orden
        order = await place_order(symbol, 'BUY', quantity, price)
        print(f"Orden colocada: {order}")

    async def open_short_position(self, symbol, price):
        """
        Abre una posición corta.

        Args:
            symbol (str): Símbolo del par de trading.
            price (float): Precio de apertura de la posición.
        """
        print(f"Abriendo posición corta para {symbol} a {price}")
        self.open_positions[symbol] = {'type': 'short', 'price': price}
        
        # Obtener el balance de la cuenta
        balance = await get_account_balance()
        
        # Calcular la cantidad a vender (por ejemplo, el 1% del balance)
        quantity = (balance * 0.01) / price
        
        # Colocar la orden
        order = await place_order(symbol, 'SELL', quantity, price)
        print(f"Orden colocada: {order}")

    async def close_position(self, symbol, price):
        """
        Cierra una posición existente.

        Args:
            symbol (str): Símbolo del par de trading.
            price (float): Precio de cierre de la posición.
        """
        position = self.open_positions.pop(symbol)
        print(f"Cerrando posición {position['type']} para {symbol} a {price}")
        
        # Obtener la cantidad de la posición abierta
        quantity = position['quantity']
        
        # Colocar la orden de cierre
        order_type = 'SELL' if position['type'] == 'long' else 'BUY'
        order = await place_order(symbol, order_type, quantity, price)
        print(f"Orden de cierre colocada: {order}")

def train_model():
    """
    Entrena el modelo de machine learning.
    """
    bot = TrainingBot()
    asyncio.run(bot.get_candles())
    bot.analyze_fluctuations()
    bot.train_model()

def evaluate_model(test_data):
    """
    Evalúa el modelo con datos de prueba.

    Args:
        test_data (dict): Datos de prueba para evaluar el modelo.

    Returns:
        dict: Métricas de evaluación del modelo.
    """
    bot = TrainingBot()
    bot.load_model("model.pkl")
    return bot.evaluate_model(test_data)