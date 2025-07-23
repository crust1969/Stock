import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime, timedelta

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

def calculate_implied_move(price, iv, days):
    if iv is None or price is None:
        return None
    move = price * iv * (days / 365) ** 0.5
    return round(move, 2)

def get_option_greeks(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    expiration_dates = ticker.options
    if not expiration_dates:
        return []

    try:
        opt_chain = ticker.option_chain(expiration_dates[0])
        calls = opt_chain.calls
        if 'impliedVolatility' in calls.columns:
            greeks = calls[['strike', 'lastPrice', 'impliedVolatility', 'delta', 'gamma', 'theta', 'vega']]
            return greeks.head(10)
        else:
            return []
    except:
        return []

# 📈 Streamlit UI

st.title("📊 Aktienanalyse – Kurs, SMA, MACD, PEG, Implied Move & Greeks")

symbol = st.text_input("Ticker eingeben (z. B. AAPL, MSFT, AMZN):", "AAPL")

if st.button("🔍 Analyse starten"):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="6mo")

        if df.empty:
            st.error("⚠️ Keine Kursdaten gefunden.")
        else:
            # 🧮 SMA & MACD
            df["SMA20"] = df["Close"].rolling(window=20).mean()
            df["SMA50"] = df["Close"].rolling(window=50).mean()
            macd, signal = calculate_macd(df)

            # 📊 Fundamentaldaten
            info = ticker.info
            current_price = info.get("currentPrice", None)
            revenue_growth = info.get("revenueGrowth", None)
            implied_vol = info.get("impliedVolatility", None)

            growth_str = f"{round(revenue_growth * 100, 2)} %" if revenue_growth else "Nicht verfügbar"

            alpha_key = st.secrets["ALPHA_VANTAGE_API_KEY"]
            peg_ratio = get_peg_from_alpha_vantage(symbol, alpha_key)

            # 💥 Implied Moves berechnen
            if current_price and implied_vol:
                weekly_move_usd = calculate_implied_move(current_price, implied_vol, 7)
                monthly_move_usd = calculate_implied_move(current_price, implied_vol, 30)

                weekly_move_pct = round(weekly_move_usd / current_price * 100, 2)
                monthly_move_pct = round(monthly_move_usd / current_price * 100, 2)

                implied_move_text = f"""
                - **Implied Weekly Move (±):** {weekly_move_usd} USD (~{weekly_move_pct} %)
                - **Implied Monthly Move (±):** {monthly_move_usd} USD (~{monthly_move_pct} %)
                """

                # 📈 Chart mit Levels anzeigen
                st.subheader("📉 Kursverlauf mit SMA20, SMA50 & Implied Move Levels")
                fig, ax = plt.subplots()
                ax.plot(df.index, df["Close"], label="Kurs", linewidth=2)
                ax.plot(df.index, df["SMA20"], label="SMA 20", linestyle="--", color="orange")
                ax.plot(df.index, df["SMA50"], label="SMA 50", linestyle="--", color="green")
                ax.axhline(current_price + weekly_move_usd, linestyle=":", color="red", label="Weekly Move +")
                ax.axhline(current_price - weekly_move_usd, linestyle=":", color="red", label="Weekly Move -")
                ax.set_title(f"{symbol} – Kurs & Implied Move")
                ax.legend()
                st.pyplot(fig)
            else:
                implied_move_text = "- **Implied Move:** Nicht verfügbar (IV fehlt)"

            st.markdown(f"""
            - **Aktueller Kurs:** {current_price} USD  
            - **PEG-Ratio:** {peg_ratio}  
            - **Umsatzwachstum (letzte 3 Jahre):** {growth_str}  
            {implied_move_text}
            """)

            # 📈 MACD anzeigen
            st.subheader("📈 MACD")
            fig2, ax2 = plt.subplots()
            ax2.plot(macd, label="MACD", color="purple")
            ax2.plot(signal, label="Signal", color="gray")
            ax2.axhline(0, linestyle="--", color="black", linewidth=1)
            ax2.set_title("MACD & Signal")
            ax2.legend()
            st.pyplot(fig2)

            # 📐 Greeks anzeigen
            st.subheader("📐 Options-Greeks (nächste Fälligkeit, Top 10 Calls)")
            greeks_df = get_option_greeks(symbol)
            if not greeks_df.empty:
                st.dataframe(greeks_df)
            else:
                st.info("Keine Optionsdaten verfügbar oder API-Fehler.")

    except Exception as e:
        st.error(f"Fehler bei der Analyse: {e}")
