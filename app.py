import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import streamlit as st

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(
    page_title="Omas Aktien-Mentor v2",
    page_icon="👵",
    layout="wide"
)

# --- DATA FETCHING ---
@st.cache_data(ttl=3600) # Cache speichert Daten für 1 Stunde
def fetch_stock_data(symbol, period="180d", interval="1d"):
    """Zieht Kursdaten von Yahoo Finance."""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period, interval=interval)
        
        if data.empty:
            return pd.DataFrame()
        return data
    except Exception as e:
        st.error(f"Verbindung zu den Börsendaten unterbrochen: {e}")
        return pd.DataFrame()

# --- FEATURE ENGINEERING (Die Big Data Logik) ---
def calculate_indicators(df):
    """Berechnet Trends und Volumen-Durchschnitte."""
    if df.empty: return df
    
    # 1. Trend: Gleitende Durchschnitte (SMA)
    df['SMA_Kurz'] = df['Close'].rolling(window=5).mean()
    df['SMA_Lang'] = df['Close'].rolling(window=15).mean()
    
    # 2. Liquidität: Volumen-Durchschnitt
    df['Vol_Durchschnitt'] = df['Volume'].rolling(window=20).mean()
    return df

# --- STRATEGIE-LOGIK ---
def generate_signals(df):
    """Erstellt ein Ampelsystem basierend auf Trends und Volumen."""
    if df.empty: return df
    
    df['Signal_Score'] = 0
    
    # Trend-Check: Kurzzeit-Trend über Langzeit-Trend?
    df.loc[df['SMA_Kurz'] > df['SMA_Lang'], 'Signal_Score'] = 1
    df.loc[df['SMA_Kurz'] <= df['SMA_Lang'], 'Signal_Score'] = -1
    
    # Volumen-Bestätigung: Ist heute besonders viel los?
    volume_ok = (df['Volume'] > df['Vol_Durchschnitt'])
    df.loc[volume_ok & (df['Signal_Score'] > 0), 'Signal_Score'] += 1
    df.loc[volume_ok & (df['Signal_Score'] < 0), 'Signal_Score'] -= 1
    
    return df

# --- VISUALISIERUNG ---
def plot_dashboard(df, symbol):
    """Erstellt einen sauberen Chart für die Anzeige."""
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Preiskurve
    ax1.plot(df.index, df['Close'], label='Aktienkurs', color='#1f77b4', lw=2)
    ax1.plot(df.index, df['SMA_Kurz'], label='Trend (kurz)', color='#ff7f0e', alpha=0.7, linestyle='--')
    ax1.set_ylabel("Preis in Dollar ($)")
    
    # Volumen als Balken im Hintergrund
    ax2 = ax1.twinx()
    ax2.bar(df.index, df['Volume'], color='gray', alpha=0.15, label='Handelsmenge')
    ax2.set_ylabel("Anzahl gehandelter Aktien")
    
    plt.title(f"Marktanalyse für {symbol}", fontsize=14)
    ax1.legend(loc='upper left')
    plt.tight_layout()
    return fig

# --- HAUPTPROGRAMM (Streamlit UI) ---
def main():
    st.title("📈 KI-Aktien-Mentor für Oma")
    st.write("Willkommen! Ich helfe dir, den Überblick an der Börse zu behalten.")

    # Top-Liste für das klickbare Band
    top_tech_companies = {
        'Apple': 'AAPL',
        'Microsoft': 'MSFT',
        'Amazon': 'AMZN',
        'Alphabet': 'GOOGL',
        'NVIDIA': 'NVDA',
        'Tesla': 'TSLA',
        'Meta': 'META',
        'Bitcoin': 'BTC-USD',
        'S&P 500': 'SPY',
        'Nasdaq': 'QQQ'
    }

    # Initialisierung des Session State für den Ticker, falls noch nicht vorhanden
    if 'current_ticker' not in st.session_state:
        st.session_state.current_ticker = "AAPL"

    # Eingabebereich in der Seitenleiste
    st.sidebar.header("Suche")
    ticker_input = st.sidebar.text_input("Welche Aktie suchst du? (Kürzel)", value=st.session_state.current_ticker).upper()
    
    # Wenn der User manuell tippt, aktualisieren wir den State
    if ticker_input != st.session_state.current_ticker:
        st.session_state.current_ticker = ticker_input

    if st.sidebar.button("Daten aktualisieren"):
        st.cache_data.clear()

    # Analyse-Start
    with st.spinner('Ich schaue kurz an der Börse nach...'):
        df = fetch_stock_data(st.session_state.current_ticker)
        
        if not df.empty and len(df) > 20:
            df = calculate_indicators(df)
            df = generate_signals(df)
            
            aktuelle_daten = df.iloc[-1]
            score = aktuelle_daten['Signal_Score']
            preis = aktuelle_daten['Close']
            
            # Anzeige-Karten
            col1, col2 = st.columns(2)
            col1.metric("Aktueller Preis", f"{preis:.2f} $")
            
            # Oma-freundliche Interpretation
            if score >= 1:
                col2.success("Empfehlung: GÜNSTIG 🟢")
                st.info("💡 **Was das bedeutet:** Die Zeichen stehen auf Wachstum und viele Leute kaufen gerade. Das sieht gut aus!")
            elif score <= -1:
                col2.warning("Empfehlung: VORSICHT 🔴")
                st.info("💡 **Was das bedeutet:** Der Trend zeigt nach unten. Vielleicht lieber noch ein bisschen abwarten mit dem Kaufen.")
            else:
                col2.info("Empfehlung: ABWARTEN 🟡")
                st.info("💡 **Was das bedeutet:** Es ist gerade ruhig an der Börse. Kein Grund zur Eile.")
                
            # Chart anzeigen
            st.pyplot(plot_dashboard(df, st.session_state.current_ticker))
            
            # --- NEUES FEATURE: Das klickbare Aktien-Band ---
            st.divider()
            st.subheader("Schnellauswahl: Klicke auf ein Unternehmen für die Analyse")
            
            # Wir erstellen mehrere Spalten für das Band
            cols = st.columns(len(top_tech_companies))
            for i, (name, sym) in enumerate(top_tech_companies.items()):
                if cols[i].button(name, key=f"btn_{sym}"):
                    st.session_state.current_ticker = sym
                    st.rerun() # App neu starten mit dem neuen Ticker
            
        else:
            st.error(f"Entschuldige, ich konnte für '{st.session_state.current_ticker}' keine Daten finden. Probiere es mal mit 'AAPL' (Apple) oder 'MSFT' (Microsoft).")

if __name__ == "__main__":
    main()
