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

def calculate_implied_move(price, iv, days):
    iv_decimal = iv / 100
    move = price * iv_decimal * (days / 365) ** 0.5
    return round(move, 2)

# 📈 Streamlit UI

st.title("📊 Aktienanalyse – Kurs, SMA, MACD, PEG & Implied Move")

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

            # 📈 Chart anzeigen
            st.subheader("📉 Kursverlauf mit SMA20 & SMA50")
            fig, ax = plt.subplots()
            ax.plot(df["Close"], label="Kurs", linewidth=2)
            ax.plot(df["SMA20"], label="SMA 20", linestyle="--", color="orange")
            ax.plot(df["SMA50"], label="SMA 50", linestyle="--", color="green")
            ax.set_title(f"{symbol} – Kurs & gleitende Durchschnitte")
            ax.legend()
            st.pyplot(fig)

            # 📉 MACD anzeigen
            st.subheader("📈 MACD")
            fig2, ax2 = plt.subplots()
            ax2.plot(macd, label="MACD", color="purple")
            ax2.plot(signal, label="Signal", color="gray")
            ax2.axhline(0, linestyle="--", color="black", linewidth=1)
            ax2.set_title("MACD & Signal")
            ax2.legend()
            st.pyplot(fig2)

            # 📊 Fundamentaldaten
            st.subheader("📊 Fundamentale Kennzahlen")

            info = ticker.info
            current_price = info.get("currentPrice", None)
            revenue_growth = info.get("revenueGrowth", None)
            iv_estimate = info.get("impliedVolatility", None)  # annualisiert

            growth_str = f"{round(revenue_growth * 100, 2)} %" if revenue_growth else "Nicht verfügbar"

            # PEG Ratio über Alpha Vantage
            alpha_key = st.secrets["ALPHA_VANTAGE_API_KEY"]
            peg_ratio = get_peg_from_alpha_vantage(symbol, alpha_key)

            # Implied Move berechnen
            if current_price and iv_estimate:
                weekly_move = calculate_implied_move(current_price, iv_estimate * 100, 7)
                monthly_move = calculate_implied_move(current_price, iv_estimate * 100, 30)
                move_text = f"""
                - **Implied Weekly Move (±):** {weekly_move} USD (~{round(weekly_move / current_price * 100, 2)} %)
                - **Implied Monthly Move (±):** {monthly_move} USD (~{round(monthly_move / current_price * 100, 2)} %)
                """
            else:
                move_text = "- **Implied Move:** Nicht verfügbar (IV fehlt)"

            st.markdown(f"""
            - **Aktueller Kurs:** {current_price} USD  
            - **PEG-Ratio:** {peg_ratio}  
            - **Umsatzwachstum (letzte 3 Jahre):** {growth_str}  
            {move_text}
            """)

    except Exception as e:
        st.error(f"Fehler bei der Analyse: {e}")
