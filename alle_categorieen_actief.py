# Vervang je ALLE_VOORZIENINGEN sectie in app.py door deze versie:

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
        'active': True  # ← Geactiveerd
    },
    'apotheek': {
        'google_types': ['pharmacy'],
        'display_name': 'Apotheek',
        'active': True  # ← Geactiveerd
    },
    'sportfaciliteiten': {
        'google_types': ['gym', 'stadium', 'bowling_alley', 'swimming_pool'],
        'display_name': 'Sportfaciliteiten',
        'active': True  # ← Geactiveerd
    },
    'horeca': {
        'google_types': ['restaurant', 'bar', 'cafe', 'meal_takeaway'],
        'display_name': 'Horeca',
        'active': True  # ← Geactiveerd
    },
    'werkgelegenheid': {
        'google_types': ['shopping_mall', 'store'],
        'display_name': 'Werkgelegenheid',
        'active': True  # ← Geactiveerd
    },
    'cultuur': {
        'google_types': ['library', 'museum', 'movie_theater', 'art_gallery'],
        'display_name': 'Cultuur',
        'active': True  # ← Geactiveerd
    },
    'groenvoorziening': {
        'google_types': ['park'],
        'display_name': 'Groenvoorziening',
        'active': True  # ← Geactiveerd
    }
}
