import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import requests

# 🏷️ Funktionen

def get_peg_from_alpha_vantage(symbol, api_key):
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("PEGRatio", "Nicht verfügbar")
    else:
        return "Fehler bei API-Abruf"

def calculate_macd(data):
    short_ema = data['Close'].ewm(span=12, adjust=False).mean()
    long_ema = data['Close'].ewm(span=26, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_implied_moves(price, iv):
    if price is None or iv is None:
        return None, None
    weekly_move = price * iv * (1 / (52 ** 0.5))  # √1/52
    monthly_move = price * iv * (1 / (12 ** 0.5)) # √1/12
    return weekly_move, monthly_move

# 📈 Streamlit UI

st.title("📊 Aktienanalyse – Kurs, SMA, MACD, RSI & PEG-Ratio")

symbol = st.text_input("Ticker eingeben (z. B. AAPL, MSFT, AMZN):", "AAPL")

if st.button("🔍 Analyse starten"):

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="6mo")

        if isinstance(df, pd.DataFrame) and df.empty:
            st.error("⚠️ Keine Kursdaten gefunden.")
        else:
            # 🧮 SMA, MACD, RSI
            df["SMA20"] = df["Close"].rolling(window=20).mean()
            df["SMA50"] = df["Close"].rolling(window=50).mean()
            macd, signal = calculate_macd(df)
            rsi = calculate_rsi(df)

            # 📉 Kurschart mit SMAs
            st.subheader("📉 Kursverlauf mit SMA20 & SMA50")
            fig, ax = plt.subplots()
            ax.plot(df.index, df["Close"], label="Kurs", linewidth=2)
            ax.plot(df.index, df["SMA20"], label="SMA 20", linestyle="--", color="orange")
            ax.plot(df.index, df["SMA50"], label="SMA 50", linestyle="--", color="green")
            ax.set_title(f"{symbol} – Kurs & gleitende Durchschnitte")
            ax.legend()
            st.pyplot(fig)

            # 📈 MACD-Chart
            st.subheader("📈 MACD")
            fig2, ax2 = plt.subplots()
            ax2.plot(df.index, macd, label="MACD", color="purple")
            ax2.plot(df.index, signal, label="Signal", color="gray")
            ax2.axhline(0, linestyle="--", color="black", linewidth=1)
            ax2.set_title("MACD & Signal")
            ax2.legend()
            st.pyplot(fig2)

            # 📊 RSI-Chart
            st.subheader("📉 RSI (Relative Strength Index)")
            fig3, ax3 = plt.subplots()
            ax3.plot(df.index, rsi, label="RSI", color="blue")
            ax3.axhline(70, color="red", linestyle="--", label="Überkauft (70)")
            ax3.axhline(30, color="green", linestyle="--", label="Überverkauft (30)")
            ax3.set_title("RSI (14 Tage)")
            ax3.legend()
            st.pyplot(fig3)

            # 📊 Fundamentaldaten
            st.subheader("📊 Fundamentale Kennzahlen")

            info = ticker.info
            current_price = info.get("currentPrice", None)
            revenue_growth = info.get("revenueGrowth", None)
            growth_str = f"{round(revenue_growth * 100, 2)} %" if revenue_growth else "Nicht verfügbar"

            alpha_key = st.secrets["ALPHA_VANTAGE_API_KEY"]
            peg_ratio = get_peg_from_alpha_vantage(symbol, alpha_key)

            iv = info.get("impliedVolatility", None)
            weekly_move, monthly_move = calculate_implied_moves(current_price, iv)

            weekly_str = f"{round(weekly_move, 2)} USD" if weekly_move else "Nicht verfügbar"
            monthly_str = f"{round(monthly_move, 2)} USD" if monthly_move else "Nicht verfügbar"

            st.markdown(f"""
            - **Aktueller Kurs:** {current_price} USD  
            - **PEG-Ratio:** {peg_ratio}  
            - **Umsatzwachstum (letzte 3 Jahre):** {growth_str}  
            - **Erwartete wöchentliche Bewegung (IV-basiert):** {weekly_str}  
            - **Erwartete monatliche Bewegung (IV-basiert):** {monthly_str}
            """)

    except Exception as e:
        st.error(f"Fehler bei der Analyse: {e}")
