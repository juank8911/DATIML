#!/bin/bash

# Crear directorios
mkdir -p ./binance_trading
mkdir -p ./api

# Crear archivos
touch ./binance_trading/__init__.py
touch ./binance_trading/binance_api.py
touch ./binance_trading/trading_strategy.py

touch ./api/__init__.py
touch ./api/app.py
touch ./api/routes.py

echo "Estructura de carpetas y archivos creada con éxito."