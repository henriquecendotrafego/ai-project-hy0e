from flask import Flask, jsonify, request
import pandas as pd
import yfinance as yf
import talib as ta
import matplotlib.pyplot as plt
import plotly.graph_objects as go

app = Flask(__name__)

# Função para calcular ATR
def calculate_atr(data, period):
    return ta.ATR(data['High'], data['Low'], data['Close'], timeperiod=period)

# Função para identificar níveis de volatilidade
def identify_volatility_levels(data, atr):
    recent_atr = atr[-1]
    historical_atr = data['ATR'].tail(100).mean()
    
    if recent_atr > historical_atr * 1.5:
        return "Alta"
    elif recent_atr < historical_atr / 1.5:
        return "Baixa"
    else:
        return "Média"

# Função para aplicar indicadores técnicos
def apply_indicators(data):
    rsi = ta.RSI(data['Close'], timeperiod=14)
    ema_20 = ta.EMA(data['Close'], timeperiod=20)
    ema_50 = ta.EMA(data['Close'], timeperiod=50)
    bollinger_bands = ta.BBANDS(data['Close'], timeperiod=20, nbdevup=2, nbdevdn=2)
    macd, macdsignal, macdhist = ta.MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)

    return {
        'RSI': rsi[-1],
        'EMA_20': ema_20[-1],
        'EMA_50': ema_50[-1],
        'Bollinger_Bands': bollinger_bands,
        'MACD': macd,
        'MACD_Signal': macdsignal,
        'MACD_Hist': macdhist
    }

# Função para analisar padrões de velas
def analyze_candle_patterns(data):
    # Implementação simplificada para demonstração
    patterns = []
    for i in range(len(data) - 20):
        if (data['Close'][i] > data['Open'][i] and 
            data['Close'][i + 1] < data['Open'][i + 1]):
            patterns.append('Martelo')
        elif (data['Close'][i] < data['Open'][i] and 
              data['Close'][i + 1] > data['Open'][i + 1]):
            patterns.append('Engolfo')
        else:
            patterns.append('Doji')
    
    return patterns

# Função para resumir análise técnica
def summarize_analysis(data, indicators, volatility_level, patterns):
    summary = {
        'Volatility': volatility_level,
        'Indicators': indicators,
        'Patterns': patterns
    }
    
    return summary

@app.route('/analyze', methods=['POST'])
def analyze():
    ticker = request.json['ticker']
    period = request.json['period']
    
    data = yf.download(ticker, period=period)
    
    atr = calculate_atr(data, 14)
    volatility_level = identify_volatility_levels(data, atr)
    
    indicators = apply_indicators(data)
    
    patterns = analyze_candle_patterns(data)
    
    summary = summarize_analysis(data, indicators, volatility_level, patterns)
    
    return jsonify(summary)

if __name__ == '__main__':
    app.run(debug=True)