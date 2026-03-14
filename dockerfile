# Schlankes Python-Image als Basis
FROM python:3.11-slim

# Arbeitsverzeichnis im Container festlegen
WORKDIR /app

# System-Abhängigkeiten für PDF-Verarbeitung (falls nötig) installieren
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Requirements kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Den restlichen Code kopieren
COPY . .

# Wir erstellen den Daten-Ordner intern
RUN mkdir -p /app/data

# Port 5005 freigeben
EXPOSE 5005

# Startbefehl
CMD ["python", "app.py"]
