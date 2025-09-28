#!/bin/bash
# ProximaScore startup script

echo "ProximaScore Stap 1 - Opstarten..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtuele omgeving niet gevonden. Installeer eerst:"
    echo "python -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Waarschuwing: .env bestand niet gevonden"
    echo "Kopieer .env.example naar .env en vul je Google API key in"
fi

# Activate virtual environment
source venv/bin/activate

# Create data directory if it doesn't exist
mkdir -p data

# Start backend
echo "Backend gestart op http://localhost:5000"
cd backend
python app.py
