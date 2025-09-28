"""
ProximaScore Backend - Verbeterde versie met debug logging
Volledig schaalbare architectuur, implementatie van 3 voorzieningen
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import requests
import json
import math
import os
import sqlite3
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Laad environment variabelen
load_dotenv('.env')
print(f"STARTUP DEBUG: .env bestand bestaat: {os.path.exists('.env')}")
print(f"STARTUP DEBUG: Werkmap: {os.getcwd()}")

# Configuratie
app = Flask(__name__, 
            template_folder='frontend',
            static_folder='frontend/static')
CORS(app)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration met uitgebreide debugging
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')
GOOGLE_PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY', GOOGLE_API_KEY)

# Debug API key configuratie
if GOOGLE_API_KEY:
    print(f"DEBUG: Geocoding API key geladen: {GOOGLE_API_KEY[:10]}... (lengte: {len(GOOGLE_API_KEY)})")
else:
    print("DEBUG: Geocoding API key: LEEG")

if GOOGLE_PLACES_API_KEY:
    print(f"DEBUG: Places API key geladen: {GOOGLE_PLACES_API_KEY[:10]}... (lengte: {len(GOOGLE_PLACES_API_KEY)})")
else:
    print("DEBUG: Places API key: LEEG")

if not GOOGLE_API_KEY:
    print("WAARSCHUWING: Geen Google API key gevonden! Controleer je .env bestand.")

# Volledige voorzieningen definitie
ALLE_VOORZIENINGEN = {
    'supermarkt': {
        'google_types': ['supermarket', 'grocery_or_supermarket'],
        'display_name': 'Supermarkt',
        'active': True
    },
    'huisarts': {
        'google_types': ['doctor', 'hospital', 'physiotherapist'],
        'display_name': 'Huisarts/Medisch centrum',
        'active': True
    },
    'openbaar_vervoer': {
        'google_types': ['bus_station', 'subway_station', 'train_station', 'transit_station'],
        'display_name': 'Openbaar vervoer',
        'active': True
    },
    'basisschool': {
        'google_types': ['primary_school', 'school'],
        'display_name': 'Basisschool',
        'active': False
    },
    'apotheek': {
        'google_types': ['pharmacy'],
        'display_name': 'Apotheek',
        'active': False
    },
    'sportfaciliteiten': {
        'google_types': ['gym', 'stadium', 'bowling_alley', 'swimming_pool'],
        'display_name': 'Sportfaciliteiten',
        'active': False
    },
    'horeca': {
        'google_types': ['restaurant', 'bar', 'cafe', 'meal_takeaway'],
        'display_name': 'Horeca',
        'active': False
    },
    'werkgelegenheid': {
        'google_types': ['shopping_mall', 'store'],
        'display_name': 'Werkgelegenheid',
        'active': False
    },
    'cultuur': {
        'google_types': ['library', 'museum', 'movie_theater', 'art_gallery'],
        'display_name': 'Cultuur',
        'active': False
    },
    'groenvoorziening': {
        'google_types': ['park'],
        'display_name': 'Groenvoorziening',
        'active': False
    }
}

# Volledige profielen definitie
# Vervang je hele ALLE_PROFIELEN sectie (rond regel 100-140) door deze versie:

ALLE_PROFIELEN = {
    'algemeen': {
        'display_name': 'Algemeen profiel',
        'gewichten': {
            'supermarkt': 35,
            'huisarts': 35,
            'openbaar_vervoer': 30,
            'basisschool': 0,
            'apotheek': 0,
            'sportfaciliteiten': 0,
            'horeca': 0,
            'werkgelegenheid': 0,
            'cultuur': 0,
            'groenvoorziening': 0
        },
        'active': True
    },
    'gezin': {
        'display_name': 'Gezin met kinderen',
        'gewichten': {
            'basisschool': 25,
            'supermarkt': 20,
            'huisarts': 15,
            'openbaar_vervoer': 15,
            'apotheek': 10,
            'sportfaciliteiten': 10,
            'groenvoorziening': 5,
            'horeca': 0,
            'werkgelegenheid': 0,
            'cultuur': 0
        },
        'active': True
    },
    'senior': {
        'display_name': 'Senior 65+',
        'gewichten': {
            'huisarts': 30,
            'apotheek': 20,
            'supermarkt': 20,
            'openbaar_vervoer': 15,
            'cultuur': 5,
            'groenvoorziening': 5,
            'horeca': 3,
            'sportfaciliteiten': 2,
            'basisschool': 0,
            'werkgelegenheid': 0
        },
        'active': True
    },
    'student': {
        'display_name': 'Student',
        'gewichten': {
            'openbaar_vervoer': 30,
            'supermarkt': 25,
            'horeca': 15,
            'sportfaciliteiten': 10,
            'cultuur': 10,
            'huisarts': 5,
            'apotheek': 5,
            'basisschool': 0,
            'werkgelegenheid': 0,
            'groenvoorziening': 0
        },
        'active': True
    },
    'starter': {
        'display_name': 'Starter op woningmarkt',
        'gewichten': {
            'openbaar_vervoer': 25,
            'supermarkt': 20,
            'huisarts': 15,
            'werkgelegenheid': 15,
            'sportfaciliteiten': 10,
            'apotheek': 5,
            'horeca': 5,
            'cultuur': 5,
            'basisschool': 0,
            'groenvoorziening': 0
        },
        'active': True
    }
}
class ProximaScoreCalculator:
    """Hoofdklasse voor ProximaScore berekeningen met uitgebreide debug logging"""
    
    def __init__(self, google_api_key):
        self.api_key = google_api_key
        self.places_api_key = GOOGLE_PLACES_API_KEY
        print(f"Calculator geinitialiseerd met API key lengte: {len(self.api_key)}")
        self.init_database()
    
    def init_database(self):
        """Initialiseer database schema"""
        db_path = Path('data/proximascore.db')
        db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS geocoding_cache (
                    id INTEGER PRIMARY KEY,
                    address_hash TEXT UNIQUE,
                    address TEXT,
                    lat REAL,
                    lng REAL,
                    created_at TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS poi_cache (
                    id INTEGER PRIMARY KEY,
                    location_hash TEXT,
                    category TEXT,
                    poi_data TEXT,
                    created_at TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS score_cache (
                    id INTEGER PRIMARY KEY,
                    address_hash TEXT,
                    profile TEXT,
                    score_data TEXT,
                    created_at TIMESTAMP
                )
            ''')
        print("Database geinitialiseerd")
    
    def geocode_address(self, address):
        """Converteer Nederlands adres naar coordinaten met debug logging"""
        print(f"Geocoding adres: {address}")
        
        try:
            # Cache check
            address_hash = hashlib.md5(address.lower().encode()).hexdigest()
            db_path = Path('data/proximascore.db')
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT lat, lng FROM geocoding_cache 
                    WHERE address_hash = ? AND created_at > ?
                ''', (address_hash, datetime.now() - timedelta(hours=24)))
                
                cached = cursor.fetchone()
                if cached:
                    print(f"Geocoding cache hit voor: {address}")
                    return {'lat': cached[0], 'lng': cached[1]}
            
            # Google Geocoding API call
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': address,
                'region': 'nl',
                'key': self.api_key
            }
            
            print(f"Geocoding API call: {url}")
            print(f"Geocoding parameters: {params}")
            
            response = requests.get(url, params=params, timeout=10)
            print(f"Geocoding response status: {response.status_code}")
            
            data = response.json()
            print(f"Geocoding API status: {data.get('status')}")
            
            if data['status'] == 'OK' and data['results']:
                location = data['results'][0]['geometry']['location']
                
                # Cache opslaan
                with sqlite3.connect(db_path) as conn:
                    conn.execute('''
                        INSERT OR REPLACE INTO geocoding_cache 
                        (address_hash, address, lat, lng, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (address_hash, address, location['lat'], location['lng'], datetime.now()))
                
                print(f"Geocoding succesvol: {address} -> {location}")
                return location
            else:
                print(f"Geocoding gefaald: {data.get('status')} - {data}")
                return None
                
        except Exception as e:
            print(f"Geocoding fout: {str(e)}")
            return None
    
    def find_nearby_places(self, lat, lng, category):
        """Zoek voorzieningen via Google Places API met uitgebreide debug logging"""
        print(f"\n=== ZOEK VOORZIENINGEN ===")
        print(f"Coordinaten: {lat:.6f}, {lng:.6f}")
        print(f"Categorie: {category}")
        print(f"Categorie actief: {ALLE_VOORZIENINGEN[category]['active']}")
        
        if not ALLE_VOORZIENINGEN[category]['active']:
            print(f"Categorie {category} niet actief in huidige stap")
            return []
        
        try:
            # Cache check
            location_hash = hashlib.md5(f"{lat:.6f},{lng:.6f}".encode()).hexdigest()
            db_path = Path('data/proximascore.db')
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT poi_data FROM poi_cache 
                    WHERE location_hash = ? AND category = ? AND created_at > ?
                ''', (location_hash, category, datetime.now() - timedelta(hours=24)))
                
                cached = cursor.fetchone()
                if cached:
                    print(f"POI cache hit voor categorie: {category}")
                    return json.loads(cached[0])
            
            # Google Places API calls
            places = []
            place_types = ALLE_VOORZIENINGEN[category]['google_types']
            print(f"Google types voor {category}: {place_types}")
            print(f"Places API key lengte: {len(self.places_api_key)}")
            
            for place_type in place_types:
                print(f"\nZoeken naar type: {place_type}")
                
                url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                params = {
                    'location': f"{lat},{lng}",
                    'radius': 2000,
                    'type': place_type,
                    'key': self.places_api_key
                }
                
                print(f"API URL: {url}")
                print(f"API Parameters: {params}")
                if self.places_api_key:
                    print(f"API key eindigt op: ...{self.places_api_key[-4:]}")
                else:
                    print("API key: LEEG")
                
                response = requests.get(url, params=params, timeout=10)
                print(f"Response status code: {response.status_code}")
                print(f"Response header Content-Type: {response.headers.get('Content-Type')}")
                
                if response.status_code != 200:
                    print(f"HTTP fout: {response.status_code}")
                    print(f"Response tekst: {response.text}")
                    continue
                
                try:
                    data = response.json()
                except Exception as e:
                    print(f"JSON parse fout: {e}")
                    print(f"Response tekst: {response.text[:500]}")
                    continue
                
                print(f"API status: {data.get('status')}")
                print(f"Resultaten gevonden: {len(data.get('results', []))}")
                
                if data.get('status') != 'OK':
                    print(f"API fout status: {data.get('status')}")
                    print(f"API fout bericht: {data.get('error_message', 'Geen foutbericht')}")
                    continue
                
                if data['status'] == 'OK':
                    place_results = data.get('results', [])
                    print(f"Verwerken van {len(place_results)} resultaten voor {place_type}")
                    
                    for place in place_results:
                        if place.get('business_status') != 'CLOSED_PERMANENTLY':
                            distance = self.calculate_distance(
                                lat, lng,
                                place['geometry']['location']['lat'],
                                place['geometry']['location']['lng']
                            )
                            
                            place_info = {
                                'name': place['name'],
                                'address': place.get('vicinity', ''),
                                'distance_meters': round(distance),
                                'lat': place['geometry']['location']['lat'],
                                'lng': place['geometry']['location']['lng'],
                                'rating': place.get('rating', 0)
                            }
                            places.append(place_info)
                            print(f"Toegevoegd: {place['name']} ({round(distance)}m)")
            
            # Sorteer op afstand, neem dichtstbijzijnde 3
            places.sort(key=lambda x: x['distance_meters'])
            places = places[:3]
            
            print(f"Totaal {len(places)} voorzieningen gevonden voor {category}")
            for place in places:
                print(f"  - {place['name']}: {place['distance_meters']}m")
            
            # Cache opslaan
            with sqlite3.connect(db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO poi_cache 
                    (location_hash, category, poi_data, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (location_hash, category, json.dumps(places), datetime.now()))
            
            print(f"=== EINDE ZOEK VOORZIENINGEN ===\n")
            return places
            
        except Exception as e:
            print(f"Places API fout voor {category}: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Bereken afstand tussen twee punten (Haversine formule)"""
        R = 6371000  # Earth radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def calculate_category_score(self, places):
        """Score voor categorie: max(0, 100 - (distance / 20))"""
        if not places:
            return 0
        
        closest_distance = min(places, key=lambda x: x['distance_meters'])['distance_meters']
        score = max(0, 100 - (closest_distance / 20))
        return min(100, score)
    
    def calculate_proxima_score(self, address, profile='algemeen'):
        """Bereken ProximaScore voor adres en profiel"""
        print(f"\n=== PROXIMASCORE BEREKENING ===")
        print(f"Adres: {address}")
        print(f"Profiel: {profile}")
        
        try:
            # Controleer of profiel actief is
            if not ALLE_PROFIELEN[profile]['active']:
                return {'error': f'Profiel {profile} nog niet beschikbaar in deze versie'}
            
            # Geocode address
            location = self.geocode_address(address)
            if not location:
                return {'error': 'Adres niet gevonden'}
            
            lat, lng = location['lat'], location['lng']
            gewichten = ALLE_PROFIELEN[profile]['gewichten']
            
            print(f"Geocoordinaten: {lat}, {lng}")
            print(f"Gebruikte gewichten: {gewichten}")
            
            # Bereken scores per categorie (alleen actieve)
            categorie_scores = {}
            total_weighted_score = 0
            total_weight = 0
            
            for category, weight in gewichten.items():
                if weight > 0 and ALLE_VOORZIENINGEN[category]['active']:
                    print(f"\nBerekenen score voor: {category} (gewicht: {weight})")
                    places = self.find_nearby_places(lat, lng, category)
                    category_score = self.calculate_category_score(places)
                    
                    categorie_scores[category] = {
                        'score': round(category_score, 1),
                        'weight': weight,
                        'places': places,
                        'display_name': ALLE_VOORZIENINGEN[category]['display_name']
                    }
                    
                    total_weighted_score += (category_score * weight)
                    total_weight += weight
                    
                    print(f"Score voor {category}: {category_score:.1f}")
            
            # Normaliseer score naar 0-100
            final_score = (total_weighted_score / total_weight) if total_weight > 0 else 0
            
            print(f"Totaal gewogen score: {total_weighted_score}")
            print(f"Totaal gewicht: {total_weight}")
            print(f"Finale score: {final_score:.1f}")
            
            result = {
                'address': address,
                'profile': profile,
                'profile_display': ALLE_PROFIELEN[profile]['display_name'],
                'total_score': round(final_score, 1),
                'location': location,
                'categories': categorie_scores,
                'calculated_at': datetime.now().isoformat(),
                'version': 'Verbeterde versie met debug logging'
            }
            
            print(f"=== PROXIMASCORE RESULTAAT: {final_score:.1f}/100 ===\n")
            return result
            
        except Exception as e:
            print(f"Score berekening fout: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': f'Berekening gefaald: {str(e)}'}

# Initialize calculator
calculator = ProximaScoreCalculator(GOOGLE_API_KEY)

# API Routes
@app.route('/')
def index():
    """Hoofdpagina - frontend"""
    return render_template('index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate_score():
    """API endpoint voor ProximaScore berekening"""
    try:
        data = request.get_json() or {}
        address = data.get('address', '').strip()
        profile = data.get('profile', 'algemeen')
        
        print(f"\nAPI CALL: /api/calculate")
        print(f"Adres: {address}")
        print(f"Profiel: {profile}")
        
        if not address:
            return jsonify({'error': 'Adres is verplicht'}), 400
        
        result = calculator.calculate_proxima_score(address, profile)
        
        if 'error' in result:
            print(f"API ERROR: {result['error']}")
            return jsonify(result), 400
        
        print(f"API SUCCESS: Score {result['total_score']}")
        return jsonify(result)
        
    except Exception as e:
        print(f"API EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Interne serverfout'}), 500

@app.route('/api/profiles')
def get_profiles():
    """Beschikbare profielen ophalen (alleen actieve)"""
    actieve_profielen = {
        key: value for key, value in ALLE_PROFIELEN.items() 
        if value['active']
    }
    return jsonify(actieve_profielen)

@app.route('/api/voorzieningen')
def get_voorzieningen():
    """Beschikbare voorzieningen ophalen (alleen actieve)"""
    actieve_voorzieningen = {
        key: value for key, value in ALLE_VOORZIENINGEN.items() 
        if value['active']
    }
    return jsonify(actieve_voorzieningen)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'google_api_configured': bool(GOOGLE_API_KEY),
        'active_categories': len([v for v in ALLE_VOORZIENINGEN.values() if v['active']]),
        'active_profiles': len([v for v in ALLE_PROFIELEN.values() if v['active']]),
        'version': 'Verbeterde versie met uitgebreide debug logging'
    })

@app.route('/api/debug/test-places', methods=['GET'])
def debug_test_places():
    """Debug endpoint om Places API direct te testen"""
    try:
        lat = float(request.args.get('lat', 51.6258671))
        lng = float(request.args.get('lng', 4.9459902))
        place_type = request.args.get('type', 'supermarket')
        
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            'location': f"{lat},{lng}",
            'radius': 2000,
            'type': place_type,
            'key': GOOGLE_PLACES_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        return jsonify({
            'url': url,
            'params': params,
            'status_code': response.status_code,
            'api_status': data.get('status'),
            'results_count': len(data.get('results', [])),
            'results': data.get('results', [])[:3]  # Eerste 3 resultaten
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("\nProximaScore Backend gestart!")
    print(f"Server: http://localhost:{port}")
    print(f"Debug mode: {debug}")
    
    api_status = "Geconfigureerd" if GOOGLE_API_KEY else "Niet gevonden"
    print(f"Google API: {api_status}")
    
    active_cats = len([v for v in ALLE_VOORZIENINGEN.values() if v['active']])
    active_profs = len([v for v in ALLE_PROFIELEN.values() if v['active']])
    print(f"Actieve categorieen: {active_cats}")
    print(f"Actieve profielen: {active_profs}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
