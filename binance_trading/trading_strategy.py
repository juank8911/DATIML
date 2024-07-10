import pandas as pd
from sklearn.model_selection import train_test_split
from binance_api import get_3h_candles, open_long_trade,get_candles
from tradingBottPr import TradingBottPr

def train_model():
    # Obtén los datos históricos de todos los tokens que sean futuros
    historical_data = get_candles()
    
    # Procesa los datos y obtiene características relevantes de todos los tokens
    all_tokens_data = pd.DataFrame(historical_data)
    
    # Divide los datos en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(all_tokens_data.drop("target_column", axis=1), all_tokens_data["target_column"], test_size=0.2)
    
    # Crea una instancia de la clase TradingBottPr
    tb = TradingBottPr()
    
    # Entrena el modelo utilizando la clase TradingBottPr
    tb.train(X_train, y_train)
    
    # Guarda el modelo entrenado
    tb.save_model("model.pkl")

def predict_trades(data):
    # Utiliza el modelo para predecir operaciones
    predictions = tb.predict(data)
    return predictions

import websockets

def trading_strategy_ml(symbol, interval, start_time):
    """
    Implementa tu estrategia de trading con machine learning.
    Args:
        symbol (str): Símbolo de las velas.
        interval (str): Intervalo de las velas.
        start_time (int): Fecha de inicio en formato UNIX.
    Returns:
        None
    """
    # Obtén los datos históricos de las velas
    historical_data = get_candles(symbol, interval, start_time)
    
    # Procesar los datos y obtener características relevantes
    df = pd.DataFrame(historical_data)
    
    # Utilizar el modelo de machine learning para predecir operaciones
    trades = predict_trades(df)
    
    # Monitorear el websocket para determinar el momento de abrir o cerrar operaciones
    async def monitor_websocket():
        async with websockets.connect('wss://stream.binance.com:9443/ws/'+symbol+'@kline_'+interval) as websocket:
            while True:
                kline = await websocket.recv()
                kline_data = json.loads(kline)
                
                if kline_data['k']['x'] == 'kline':
                    if kline_data['k']['s'] == symbol and kline_data['k']['i'] == interval:
                        if kline_data['k']['c'] == trades[0]:
                            open_long_trade(symbol)
                            trades.pop(0)
                        elif kline_data['k']['c'] == trades[0]:
                            open_short_trade(symbol)
                            trades.pop(0)
                        
    asyncio.run(monitor_websocket())
    
    
# Función para evaluar el modelo
def evaluate_model(model, test_data):
    # Lógica para evaluar el modelo con datos de prueba
    print("Evaluando el modelo...")
    
    # Inicializar variables para contear ganancias
    total_ganancia = 0
    num_operaciones = 0
    
    # Recorrer los datos de prueba
    for i in range(1, len(test_data)):
        # Obtener la predicción del modelo para el dato actual
        prediction = model.predict(test_data.iloc[[i]])[0]
        
        # Obtener el valor actual de la criptomoneda
        actual_value = test_data.loc[i, 'close']
        
        # Comprobar si la predicción indica una operación larga o corta
        if prediction > actual_value:
            # Abrir una operación larga
            open_long_trade(test_data.loc[i, 'symbol'])
            num_operaciones += 1
        elif prediction < actual_value:
            # Abrir una operación corta
            open_short_trade(test_data.loc[i, 'symbol'])
            num_operaciones += 1
        else:
            # No hay operación
            pass
        
        # Comprobar si la operación ha sido cerrada
        if test_data.loc[i, 'close'] > test_data.loc[i-1, 'close'] * 1.005 or test_data.loc[i, 'close'] < test_data.loc[i-1, 'close'] * 0.995:
            # Cerrar la operación
            close_trade(test_data.loc[i, 'symbol'])
            total_ganancia += test_data.loc[i, 'close'] - test_data.loc[i-1, 'close']
        
    # Calcular la ganancia promedio
    if num_operaciones == 0:
        ganancia_promedio = 0
    else:
        ganancia_promedio = total_ganancia / num_operaciones
    
    # Imprimir los resultados de la evaluación
    print(f"Ganancia promedio: {ganancia_promedio:.2f}%")

# Carga el modelo entrenado
tb = TradingBottPr()
tb.load_model("model.pkl")
