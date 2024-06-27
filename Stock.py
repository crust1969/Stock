import streamlit as st
import requests

# Funktion zur Abfrage des Börsenkurses über Alpha Vantage
def get_stock_price(symbol):
    api_key = 'UG00QA13BAV7LYDD'
    url = f'https://www.alphavantage.co/query'
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    if 'Global Quote' in data:
        return data['Global Quote']['05. price']
    else:
        return None

# Streamlit App
def main():
    st.title('Börsenkurs Abfrage über Alpha Vantage')
    
    # Eingabefeld für das Unternehmen
    symbol = st.text_input('Geben Sie das Tickersymbol des Unternehmens ein (z.B. AAPL für Apple):')
    
    if symbol:
        # Button zum Abfragen des Börsenkurses
        if st.button('Börsenkurs abrufen'):
            st.write(f'Aktueller Börsenkurs für {symbol}:')
            price = get_stock_price(symbol)
            if price:
                st.write(f'${price}')
            else:
                st.write('Keine Daten gefunden. Bitte überprüfen Sie das Symbol und versuchen Sie es erneut.')
    
if __name__ == '__main__':
    main()
 
 
