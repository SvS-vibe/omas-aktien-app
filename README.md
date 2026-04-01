# omas-aktien-app
KI-basierter Aktien-Mentor für meine Oma mit Streamlit
👵 Omas KI-Aktien-Assistent (Nexus-Project)

Dieses Projekt wurde im Rahmen der Ausbildung zum KI-Manager entwickelt. Ziel ist es, die Brücke zwischen komplexen Finanzmarktdaten und einer benutzerfreundlichen, ethisch verantwortungsvollen Anlageberatung zu schlagen.

🚀 Vision

Aktienmärkte produzieren gigantische Mengen an Daten pro Sekunde. Für Privatpersonen – insbesondere für die ältere Generation wie meine Oma – ist dieses "Rauschen" oft überfordernd. Unser Tool nutzt Big Data Engineering und technische Indikatoren, um dieses Chaos zu strukturieren und klare, verständliche Handlungsempfehlungen auszusprechen.

📊 Big Data & KI Features

Das Tool basiert auf den Kernkonzepten der KI-Strategie:

Volume & Velocity: Echtzeit-Verarbeitung von Börsendaten über die Yahoo Finance API.

Feature Engineering: Berechnung von gleitenden Durchschnitten (SMA 5/15) und Volumen-Trends.

Value: Transformation von Rohdaten in ein einfaches Ampelsystem (Kaufen/Verkaufen).

Human-in-the-Loop: Die KI unterstützt die Entscheidung, ersetzt aber nicht die menschliche Intuition.

🛠 Installation & Start

Um die App lokal zu starten oder auf Streamlit zu hosten, werden folgende Komponenten benötigt:

Repository klonen:

git clone [https://github.com/DEIN-USERNAME/omas-aktien-app.git](https://github.com/DEIN-USERNAME/omas-aktien-app.git)


Abhängigkeiten installieren:

pip install -r requirements.txt


App starten:

streamlit run app.py


🧩 Technischer Stack

Python: Die Basis für unsere Logik.

Streamlit: Framework für das Web-Interface.

yFinance: Datenquelle für Big Data Marktdaten.

Matplotlib: Visualisierung der Trends.

📝 Rechtlicher Hinweis

Dieses Tool dient zu Bildungszwecken im Rahmen einer Gruppenarbeit. Es stellt keine professionelle Anlageberatung dar.

Entwickelt mit Leidenschaft für datengetriebene Entscheidungen und Benutzerfreundlichkeit.
