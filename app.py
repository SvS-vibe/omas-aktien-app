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
    """Zieht Kursdaten von Yahoo Finance. Die Session-Logik wurde entfernt, da YF dies nun intern regelt."""
    try:
        # Wir rufen yfinance direkt auf, ohne manuelle Requests-Session
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
    st.title("👵 Omas KI-Aktien-Assistent")
    st.write("Willkommen! Ich helfe dir, den Überblick an der Börse zu behalten.")

    # Eingabebereich in der Seitenleiste
    st.sidebar.header("Suche")
    ticker = st.sidebar.text_input("Welche Aktie suchst du? (Kürzel)", value="AAPL").upper()
    
    if st.sidebar.button("Daten aktualisieren"):
        st.cache_data.clear()

    # Analyse-Start
    with st.spinner('Ich schaue kurz an der Börse nach...'):
        df = fetch_stock_data(ticker)
        
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
            st.pyplot(plot_dashboard(df, ticker))
            
        else:
            st.error("Entschuldige, ich konnte für dieses Kürzel keine Daten finden. Probiere es mal mit 'AAPL' (Apple) oder 'MSFT' (Microsoft).")

if __name__ == "__main__":
    main()
