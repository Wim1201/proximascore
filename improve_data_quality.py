#!/usr/bin/env python3
"""
Data Quality Improvement Script voor ProximaScore
Verbetert Google Places API categorieën en filtering logica
"""

import re
import shutil
import os
from datetime import datetime

def backup_app_file():
    """Maak backup van huidige app.py"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"app_backup_{timestamp}.py"
    
    shutil.copy2("app.py", backup_name)
    print(f"✓ Backup gemaakt: {backup_name}")
    return backup_name

def improve_google_places_types():
    """Verbeter de Google Places types voor betere data kwaliteit"""
    
    improvements = {
        # Problematische categorieën vervangen
        'werkgelegenheid': {
            'old': "['shopping_mall', 'store']",
            'new': "['store', 'establishment']",  # Meer specifiek
            'reason': "Minder noise, meer relevante bedrijven"
        },
        
        'sportfaciliteiten': {
            'old': "['gym', 'stadium', 'bowling_alley', 'swimming_pool']",
            'new': "['gym', 'stadium', 'bowling_alley']",  # Swimming pool eruit
            'reason': "Swimming pool geeft te veel irrelevante resultaten"
        },
        
        'cultuur': {
            'old': "['library', 'museum', 'movie_theater', 'art_gallery']",
            'new': "['library', 'museum', 'movie_theater', 'art_gallery', 'tourist_attraction']",
            'reason': "Tourist attractions toegevoegd voor betere coverage"
        }
    }
    
    # Lees huidige app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pas verbeteringen toe
    for category, improvement in improvements.items():
        old_pattern = f"'{category}': {{[^}}]*'google_types': {re.escape(improvement['old'])}"
        new_replacement = f"'{category}': {{\n        'google_types': {improvement['new']}"
        
        # Zoek en vervang
        pattern = f"('{category}': {{[^}}]*)'google_types': {re.escape(improvement['old'])}"
        replacement = f"\\1'google_types': {improvement['new']}"
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            print(f"✓ {category}: {improvement['reason']}")
        else:
            print(f"⚠ {category}: Patroon niet gevonden")
    
    # Schrijf terug naar app.py
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

def add_data_quality_filters():
    """Voeg data kwaliteit filters toe aan find_nearby_places functie"""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Zoek de plaats om quality filters toe te voegen
    # Na: if place.get('business_status') != 'CLOSED_PERMANENTLY':
    
    old_filter = """if place.get('business_status') != 'CLOSED_PERMANENTLY':"""
    
    new_filter = """if place.get('business_status') != 'CLOSED_PERMANENTLY':
                            # Data quality filters
                            if not is_place_relevant(place, category):
                                continue
                                
                            # Distance validation
                            if distance < 10:  # Te dichtbij, waarschijnlijk fout
                                print(f"⚠ Locatie te dichtbij genegeerd: {place['name']} ({round(distance)}m)")
                                continue
                            
                            if distance > 5000:  # Te ver, waarschijnlijk fout
                                print(f"⚠ Locatie te ver genegeerd: {place['name']} ({round(distance)}m)")
                                continue"""
    
    if old_filter in content:
        content = content.replace(old_filter, new_filter)
        print("✓ Distance validation toegevoegd")
    else:
        print("⚠ Kon filter locatie niet vinden")
    
    # Voeg de is_place_relevant functie toe
    relevance_function = """
def is_place_relevant(place, category):
    \"\"\"Check of een place relevant is voor de gegeven categorie\"\"\"
    place_name = place.get('name', '').lower()
    place_types = place.get('types', [])
    rating = place.get('rating', 0)
    user_ratings_total = place.get('user_ratings_total', 0)
    
    # Minimum kwaliteit eisen
    if rating > 0 and rating < 3.0:
        return False
    
    if user_ratings_total > 0 and user_ratings_total < 3:
        return False
    
    # Categorie-specifieke relevantie checks
    if category == 'apotheek':
        relevant_words = ['apotheek', 'pharmacy', 'apotheke', 'farmacie']
        return any(word in place_name for word in relevant_words)
    
    elif category == 'huisarts':
        relevant_words = ['huisarts', 'dokter', 'arts', 'doctor', 'medisch', 'gezondheid', 'fysi']
        return any(word in place_name for word in relevant_words)
    
    elif category == 'basisschool':
        relevant_words = ['school', 'onderwijs', 'basisschool', 'elementary']
        irrelevant_words = ['rijschool', 'dansschool', 'muziekschool', 'driving']
        has_relevant = any(word in place_name for word in relevant_words)
        has_irrelevant = any(word in place_name for word in irrelevant_words)
        return has_relevant and not has_irrelevant
    
    elif category == 'sportfaciliteiten':
        relevant_words = ['gym', 'sport', 'fitness', 'zwembad', 'tennis', 'voetbal', 'hockey']
        return any(word in place_name for word in relevant_words)
    
    # Voor andere categorieën: altijd relevant (voorlopig)
    return True
"""
    
    # Voeg functie toe na de imports maar voor de class definitie
    import_end = content.find('load_dotenv(')
    if import_end > 0:
        # Vind het einde van de import sectie
        insert_pos = content.find('\n\n# Laad environment variabelen')
        if insert_pos > 0:
            content = content[:insert_pos] + relevance_function + content[insert_pos:]
            print("✓ Relevantie filter functie toegevoegd")
        else:
            print("⚠ Kon invoegpositie niet vinden voor relevantie functie")
    
    # Schrijf terug
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

def add_duplicate_removal():
    """Verbeter duplicate removal logica"""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vervang de huidige duplicate removal
    old_sort = """# Sorteer op afstand, neem dichtstbijzijnde 3
            places.sort(key=lambda x: x['distance_meters'])
            places = places[:3]"""
    
    new_sort = """# Remove duplicates gebaseerd op naam en locatie
            unique_places = []
            seen_names = set()
            
            for place in places:
                # Normalize naam voor duplicate detection
                normalized_name = place['name'].lower().strip()
                location_key = f"{place['lat']:.6f},{place['lng']:.6f}"
                unique_key = f"{normalized_name}_{location_key}"
                
                if unique_key not in seen_names:
                    unique_places.append(place)
                    seen_names.add(unique_key)
                else:
                    print(f"⚠ Duplicate weggehaald: {place['name']}")
            
            # Sorteer op afstand, neem dichtstbijzijnde 3
            unique_places.sort(key=lambda x: x['distance_meters'])
            places = unique_places[:3]"""
    
    if old_sort in content:
        content = content.replace(old_sort, new_sort)
        print("✓ Verbeterde duplicate removal toegevoegd")
    else:
        print("⚠ Kon sort locatie niet vinden")
    
    # Schrijf terug
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    """Voer alle data quality verbeteringen uit"""
    print("🔧 ProximaScore Data Quality Improvement")
    print("=" * 50)
    
    # Check of app.py bestaat
    if not os.path.exists('app.py'):
        print("❌ app.py niet gevonden in huidige directory")
        return False
    
    try:
        # Maak backup
        backup_file = backup_app_file()
        
        # Pas verbeteringen toe
        print("\n📊 Verbeter Google Places types...")
        improve_google_places_types()
        
        print("\n🎯 Voeg relevantie filters toe...")
        add_data_quality_filters()
        
        print("\n🗑️ Verbeter duplicate removal...")
        add_duplicate_removal()
        
        print(f"\n✅ Data quality verbeteringen toegepast!")
        print(f"📁 Backup beschikbaar: {backup_file}")
        print("\n🚀 Test je app met: python app.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Fout tijdens uitvoering: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
