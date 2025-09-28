# ProximaScore - Stap 1 Setup

## Wat je hebt gebouwd

Backend API met 3 actieve voorzieningen (supermarkt, huisarts, openbaar vervoer) en frontend interface. Volledige architectuur aanwezig voor toekomstige uitbreidingen.

## Vereisten

- Python 3.8+
- Google Cloud API key met Geocoding en Places API toegang
- Internet verbinding voor API calls

## Installatie

1. **Project setup**
   ```bash
   cd proximascore
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment configuratie**
   ```bash
   cp .env.example .env
   # Bewerk .env en vul je Google API key in
   ```

3. **Start applicatie**
   ```bash
   cd backend
   python app.py
   ```

4. **Test applicatie**
   - Open http://localhost:5000
   - Voer test adres in: "Markt 1, Dongen"
   - Bekijk health check: http://localhost:5000/api/health

## API Endpoints

- `POST /api/calculate` - Bereken ProximaScore
- `GET /api/profiles` - Beschikbare profielen (alleen 'algemeen' actief)
- `GET /api/voorzieningen` - Actieve voorzieningen
- `GET /api/health` - Systeem status

## Troubleshooting

**"Geocoding failed"**: Controleer Google API key in .env
**"Places API error"**: Activeer Places API in Google Cloud Console
**Database errors**: Controleer schrijfrechten in /data map

## Wat werkt in Stap 1

- Adres geocoding voor Nederland
- 3 voorziening categorieën actief
- Afstandsberekening en scoring
- SQLite caching
- Frontend interface
- API health monitoring

## Volgende stappen (Stap 2-5)

Database en code architectuur ondersteunen al:
- Alle 10 voorziening categorieën
- 8 gebruikersprofielen
- Milieu data integratie
- AI tekst generatie
- Uitgebreide analyse

Activering gebeurt via configuratie aanpassingen in latere stappen.

## Development notes

- Test data cache in `/data/proximascore.db`
- Google API calls worden gecached voor 24 uur
- Frontend heeft development features op localhost
- Backend draait in debug mode bij FLASK_ENV=development
