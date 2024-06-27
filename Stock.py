{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "18684516-dd79-4fa5-b79b-8b129f38dc6c",
   "metadata": {},
   "outputs": [],
   "source": [
    "import streamlit as st\n",
    "import requests\n",
    "\n",
    "# Funktion zur Abfrage des Börsenkurses über Alpha Vantage\n",
    "def get_stock_price(symbol):\n",
    "    api_key = 'UG00QA13BAV7LYDD'\n",
    "    url = f'https://www.alphavantage.co/query'\n",
    "    params = {\n",
    "        'function': 'GLOBAL_QUOTE',\n",
    "        'symbol': symbol,\n",
    "        'apikey': api_key\n",
    "    }\n",
    "    response = requests.get(url, params=params)\n",
    "    data = response.json()\n",
    "    if 'Global Quote' in data:\n",
    "        return data['Global Quote']['05. price']\n",
    "    else:\n",
    "        return None\n",
    "\n",
    "# Streamlit App\n",
    "def main():\n",
    "    st.title('Börsenkurs Abfrage über Alpha Vantage')\n",
    "    \n",
    "    # Eingabefeld für das Unternehmen\n",
    "    symbol = st.text_input('Geben Sie das Tickersymbol des Unternehmens ein (z.B. AAPL für Apple):')\n",
    "    \n",
    "    if symbol:\n",
    "        # Button zum Abfragen des Börsenkurses\n",
    "        if st.button('Börsenkurs abrufen'):\n",
    "            st.write(f'Aktueller Börsenkurs für {symbol}:')\n",
    "            price = get_stock_price(symbol)\n",
    "            if price:\n",
    "                st.write(f'${price}')\n",
    "            else:\n",
    "                st.write('Keine Daten gefunden. Bitte überprüfen Sie das Symbol und versuchen Sie es erneut.')\n",
    "    \n",
    "if __name__ == '__main__':\n",
    "    main()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "76ea3673-397d-4fb2-b67e-3365c711e787",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
