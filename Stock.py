import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# App Titel
st.title("📊 Aktienanalyse mit Kurs, SMA, MACD & Kennzahlen")

# Ticker-Eingabe
symbol = st.text_input("Gib das Aktiensymbol ein (z. B. AAPL, MSFT, SAP.DE):", "AAPL")

if st.button("🔍 Analyse starten"):

    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="6mo")

        if hist.empty:
            st.error("❌ Keine Daten gefunden. Ticker überprüfen.")
        else:
            # 🔹 Aktueller Kurs
            current_price = hist["Close"].iloc[-1]
            st.subheader(f"📈 Aktueller Kurs von {symbol}: {current_price:.2f} USD")

            # 🔹 SMA20 und SMA50
            hist["SMA20"] = hist["Close"].rolling(window=20).mean()
            hist["SMA50"] = hist["Close"].rolling(window=50).mean()

            # 🔹 MACD berechnen
            ema12 = hist["Close"].ewm(span=12, adjust=False).mean()
            ema26 = hist["Close"].ewm(span=26, adjust=False).mean()
            hist["MACD"] = ema12 - ema26
            hist["Signal"] = hist["MACD"].ewm(span=9, adjust=False).mean()

            # 🔹 Diagramm: Kurs, SMA20, SMA50
            st.subheader("📉 Kursverlauf mit SMA20 & SMA50")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(hist["Close"], label="Kurs", linewidth=2)
            ax.plot(hist["SMA20"], label="SMA20", linestyle="--", color="orange")
            ax.plot(hist["SMA50"], label="SMA50", linestyle="--", color="green")
            ax.set_title(f"Kurs, SMA20 & SMA50 für {symbol}")
            ax.legend()
            st.pyplot(fig)

            # 🔹 MACD anzeigen
            st.subheader("📊 MACD (Moving Average Convergence Divergence)")
            st.line_chart(hist[["MACD", "Signal"]].dropna())

            # 🔹 Fundamentale Kennzahlen
            info = ticker.info
            peg = info.get("pegRatio", "Nicht verfügbar")
            revenue_growth = info.get("revenueGrowth", None)

            st.subheader("📌 Kennzahlen")
            st.markdown(f"**PEG-Ratio:** {peg}")
            if revenue_growth is not None:
                st.markdown(f"**Umsatzwachstum aktuell:** {revenue_growth * 100:.2f}%")
            else:
                st.markdown("**Umsatzwachstum aktuell:** Nicht verfügbar")

            # Umsatzentwicklung der letzten 3 Jahre
            try:
                fin = ticker.financials.T
                sales = fin["Total Revenue"].dropna().tail(4)
                growths = sales.pct_change().dropna()
                avg_growth = growths.mean()
                st.markdown(f"**Ø Umsatzwachstum 3 Jahre:** {avg_growth * 100:.2f}%")
            except:
                st.markdown("**Ø Umsatzwachstum 3 Jahre:** Nicht verfügbar")

    except Exception as e:
        st.error(f"Fehler: {e}")
