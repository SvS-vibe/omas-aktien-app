import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import matplotlib.ticker as mticker
import streamlit as st

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(page_title="Aktien-Analyse-Mentor", layout="wide", initial_sidebar_state="expanded")

# --- DATA FETCHING (mit Cache für bessere Performance) ---
@st.cache_data
def fetch_stock_data(symbol, period="180d", interval="1d"):
    """Zieht Daten von Yahoo Finance."""
    stock = yf.Ticker(symbol)
    data = stock.history(period=period, interval=interval)
    return data

# --- INDICATOR CALCULATION ---
def calculate_indicators(df):
    """Berechnet SMAs und Volumen-Indikatoren."""
    df['SMA_5'] = df['Close'].rolling(window=5).mean()
    df['SMA_15'] = df['Close'].rolling(window=15).mean()
    df['Volume_SMA_20'] = df['Volume'].rolling(window=20).mean()
    return df

# --- SIGNAL GENERATION ---
def generate_signals(df):
    """Kombiniert SMA-Crossover mit Volumenbestätigung."""
    df['Signal'] = 0
    # Basis: SMA Crossover
    df.loc[df['SMA_5'] > df['SMA_15'], 'Signal'] = 1
    df.loc[df['SMA_5'] <= df['SMA_15'], 'Signal'] = -1

    # Volumen-Bestätigung (+/- 1 Punkt Extra)
    volume_condition = (df['Volume'].notna()) & (df['Volume_SMA_20'].notna()) & (df['Volume'] > df['Volume_SMA_20'])
    df.loc[volume_condition & (df['Signal'] > 0), 'Signal'] += 1
    df.loc[volume_condition & (df['Signal'] < 0), 'Signal'] -= 1
    return df

# --- PLOTTING ---
def plot_data(df, symbol):
    """Erstellt den kombinierten Preis- und Volumen-Chart."""
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Preis-Achse
    ax1.plot(df.index, df['Close'], label='Schlusskurs', color='blue', alpha=0.6, lw=2)
    ax1.plot(df.index, df['SMA_5'], label='SMA 5 (Kurz)', color='orange', linestyle='--')
    ax1.plot(df.index, df['SMA_15'], label='SMA 15 (Lang)', color='green', linestyle='--')
    ax1.set_ylabel("Preis (USD)", color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True, alpha=0.3)

    # Volumen-Achse (Twin)
    ax2 = ax1.twinx()
    max_volume = df['Volume'].max()
    scale, unit = (1e9, "Mrd.") if max_volume >= 1e9 else (1e6, "Mio.") if max_volume >= 1e6 else (1, "")
    
    ax2.bar(df.index, df['Volume'] / scale, label=f'Volumen ({unit})', color='gray', alpha=0.2)
    ax2.set_ylabel(f"Volumen ({unit})", color='gray')
    ax2.tick_params(axis='y', labelcolor='gray')
    ax2.set_ylim(bottom=0)

    plt.title(f"Analyse für {symbol} (Letzte 180 Tage)")
    
    # Kombinierte Legende
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.tight_layout()
    return fig

# --- STREAMLIT UI ---
def main():
    st.title("📈 KI-Aktien-Mentor für Oma")
    st.markdown("""
    Willkommen beim Aktien-Check! Dieses Tool nutzt **Big Data Indikatoren**, um Trends zu erkennen.
    Wähle links eine Aktie aus, um die Analyse zu starten.
    """)

    # Sidebar für Auswahl
    top_tech_companies = {
        'Apple (AAPL)': 'AAPL',
        'Microsoft (MSFT)': 'MSFT',
        'Amazon (AMZN)': 'AMZN',
        'Alphabet (GOOGL)': 'GOOGL',
        'NVIDIA (NVDA)': 'NVDA',
        'Tesla (TSLA)': 'TSLA',
        'Meta Platforms (META)': 'META',
        'Bitcoin (BTC-USD)': 'BTC-USD',
        'S&P 500 (SPY)': 'SPY'
    }

    st.sidebar.header("Konfiguration")
    selected_name = st.sidebar.selectbox("Welche Aktie möchtest du prüfen?", list(top_tech_companies.keys()))
    ticker = top_tech_companies[selected_name]
    
    if st.sidebar.button("Analyse aktualisieren"):
        st.cache_data.clear()

    # Analyse ausführen
    with st.spinner(f'Analysiere {ticker}...'):
        df = fetch_stock_data(ticker)
        
        if not df.empty:
            df = calculate_indicators(df)
            df = generate_signals(df)
            last_score = df['Signal'].iloc[-1]
            last_price = df['Close'].iloc[-1]

            # Anzeige der Ergebnisse in Spalten (Metriken)
            col1, col2, col3 = st.columns(3)
            col1.metric("Aktueller Preis", f"{last_price:.2f} $")
            
            if last_score > 0:
                col2.success("Empfehlung: KAUFEN")
                st.info("💡 **Grund:** Ein positiver Trend wurde erkannt. Das Handelsvolumen bestätigt das Interesse der Käufer.")
            elif last_score < 0:
                col2.warning("Empfehlung: VERKAUFEN / HALTEN")
                st.info("💡 **Grund:** Der Trend zeigt aktuell eher nach unten. Vorsicht ist geboten.")
            else:
                col2.info("Empfehlung: NEUTRAL")

            # Chart anzeigen
            fig = plot_data(df, ticker)
            st.pyplot(fig)
            
            # Daten-Einblick (optional für Technik-Interessierte)
            with st.expander("Rohdaten anzeigen"):
                st.dataframe(df.tail(10))
        else:
            st.error("Keine Daten gefunden. Bitte versuche es später erneut.")

if __name__ == "__main__":
    main()
