import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
from .binance_api import get_candles

class TrainingBot:
    """
    Clase para entrenar y evaluar un modelo de machine learning para trading.
    """

    def __init__(self):
        self.candles_data = None
        self.analyzed_data = {}
        self.model = None

    async def get_candles(self):
        """
        Obtiene los datos de velas de las últimas 3 horas en intervalos de 1 minuto.
        """
        self.candles_data = await get_candles()

    def analyze_fluctuations(self):
        """
        Analiza las fluctuaciones de cada símbolo según las reglas especificadas.
        """
        for symbol_data in self.candles_data:
            symbol_name = symbol_data['symbol']['name']
            candles = symbol_data['symbol']['data']
            
            upward_count = 0
            downward_count = 0
            
            for i in range(len(candles) - 30):
                start_price = float(candles[i]['precio_apertura'])
                for minutes in range(1, 31):
                    end_price = float(candles[i + minutes]['precio_cierre'])
                    fluctuation = abs((end_price - start_price) / start_price * 100)
                    required_fluctuation = minutes * 0.5
                    
                    if fluctuation >= required_fluctuation:
                        if end_price > start_price:
                            upward_count += 1
                        else:
                            downward_count += 1
                        break
            
            trend = self.determine_trend(candles)
            
            self.analyzed_data[symbol_name] = {
                'upward_count': upward_count,
                'downward_count': downward_count,
                'trend': trend,
                'last_price': float(candles[-1]['precio_cierre']),
                'symbol_data': symbol_data['symbol']
            }

    def determine_trend(self, candles):
        """
        Determina si el símbolo está en una tendencia alcista o bajista.

        Args:
            candles (list): Lista de velas con datos de precios.

        Returns:
            str: 'alcista' o 'bajista' según la tendencia determinada.
        """
        short_term_ma = sum(float(candle['precio_cierre']) for candle in candles[-20:]) / 20
        long_term_ma = sum(float(candle['precio_cierre']) for candle in candles[-50:]) / 50
        return 'alcista' if short_term_ma > long_term_ma else 'bajista'

    def prepare_data_for_model(self, symbol_data):
        """
        Prepara los datos para el modelo de machine learning.

        Args:
            symbol_data (dict): Datos del símbolo incluyendo velas históricas.

        Returns:
            tuple: (X, y) donde X son las características y y es la variable objetivo.
        """
        df = pd.DataFrame(symbol_data['data'])
        df['precio_apertura'] = df['precio_apertura'].astype(float)
        df['precio_cierre'] = df['precio_cierre'].astype(float)
        df['precio_maximo'] = df['precio_maximo'].astype(float)
        df['precio_minimo'] = df['precio_minimo'].astype(float)
        df['volumen'] = df['volumen'].astype(float)

        df['SMA_20'] = df['precio_cierre'].rolling(window=20).mean()
        df['SMA_50'] = df['precio_cierre'].rolling(window=50).mean()
        df['RSI'] = self.calculate_rsi(df['precio_cierre'])
        
        df['target'] = (df['precio_cierre'].shift(-1) > df['precio_cierre']).astype(int)
        
        df = df.dropna()
        
        features = ['precio_apertura', 'precio_cierre', 'precio_maximo', 'precio_minimo', 'volumen', 'SMA_20', 'SMA_50', 'RSI']
        X = df[features]
        y = df['target']
        
        return X, y

    def calculate_rsi(self, prices, period=14):
        """
        Calcula el indicador RSI (Relative Strength Index).

        Args:
            prices (pd.Series): Serie de precios.
            period (int): Período para el cálculo del RSI.

        Returns:
            pd.Series: Serie con los valores del RSI calculados.
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def train_model(self):
        """
        Entrena el modelo de machine learning usando los datos analizados.
        Guarda el modelo entrenado en un archivo 'model.pkl'.
        """
        all_X = []
        all_y = []
        
        for symbol, data in self.analyzed_data.items():
            X, y = self.prepare_data_for_model(data['symbol_data'])
            all_X.append(X)
            all_y.append(y)
        
        X = pd.concat(all_X)
        y = pd.concat(all_y)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1-score: {f1:.4f}")
        
        joblib.dump(self.model, "model.pkl")

    def load_model(self, filename):
        """
        Carga un modelo entrenado desde un archivo.

        Args:
            filename (str): Nombre del archivo que contiene el modelo guardado.
        """
        self.model = joblib.load(filename)

    def predict_trades(self, data):
        """
        Utiliza el modelo para predecir operaciones.

        Args:
            data (dict): Datos del símbolo para realizar la predicción.

        Returns:
            np.array: Array de predicciones (0 o 1 para cada punto de datos).
        """
        X, _ = self.prepare_data_for_model(data)
        return self.model.predict(X)

    def evaluate_model(self, test_data):
        """
        Evalúa el modelo con datos de prueba.

        Args:
            test_data (dict): Datos de prueba para evaluar el modelo.

        Returns:
            dict: Métricas de evaluación del modelo.
        """
        X, y = self.prepare_data_for_model(test_data)
        y_pred = self.model.predict(X)
        
        return {
            'accuracy': accuracy_score(y, y_pred),
            'precision': precision_score(y, y_pred),
            'recall': recall_score(y, y_pred),
            'f1_score': f1_score(y, y_pred)
        }