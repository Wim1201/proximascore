#!/usr/bin/env python3
"""
Quick fix voor distance validation bug in ProximaScore
"""

import re
import shutil
from datetime import datetime

def fix_distance_validation():
    """Fix de distance validation bug"""
    
    # Backup maken
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"app_backup_bugfix_{timestamp}.py"
    shutil.copy2("app.py", backup_name)
    print(f"Backup gemaakt: {backup_name}")
    
    # Lees huidige app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Zoek het problematische gedeelte en fix het
    # Het probleem: distance check gebeurt voor distance wordt berekend
    
    problematic_code = """if place.get('business_status') != 'CLOSED_PERMANENTLY':
                            # Data quality filters
                            if not is_place_relevant(place, category):
                                continue
                                
                            # Distance validation
                            if distance < 10:  # Te dichtbij, waarschijnlijk fout
                                print(f"⚠ Locatie te dichtbij genegeerd: {place['name']} ({round(distance)}m)")
                                continue
                            
                            if distance > 5000:  # Te ver, waarschijnlijk fout
                                print(f"⚠ Locatie te ver genegeerd: {place['name']} ({round(distance)}m)")
                                continue
                            
                            distance = self.calculate_distance("""
    
    fixed_code = """if place.get('business_status') != 'CLOSED_PERMANENTLY':
                            # Bereken distance eerst
                            distance = self.calculate_distance(
                                lat, lng,
                                place['geometry']['location']['lat'],
                                place['geometry']['location']['lng']
                            )
                            
                            # Distance validation
                            if distance < 10:  # Te dichtbij, waarschijnlijk fout
                                print(f"⚠ Locatie te dichtbij genegeerd: {place['name']} ({round(distance)}m)")
                                continue
                            
                            if distance > 5000:  # Te ver, waarschijnlijk fout
                                print(f"⚠ Locatie te ver genegeerd: {place['name']} ({round(distance)}m)")
                                continue
                            
                            # Data quality filters
                            if not is_place_relevant(place, category):
                                continue"""
    
    # Ook de dubbele distance berekening wegwerken
    if problematic_code in content:
        content = content.replace(problematic_code, fixed_code)
        print("✓ Distance validation bug gefixed")
    else:
        # Alternatieve fix via regex
        pattern = r"if place\.get\('business_status'\) != 'CLOSED_PERMANENTLY':\s*# Data quality filters.*?distance = self\.calculate_distance\("
        replacement = """if place.get('business_status') != 'CLOSED_PERMANENTLY':
                            # Bereken distance eerst
                            distance = self.calculate_distance("""
        
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        print("✓ Distance validation bug gefixed (via regex)")
    
    # Verwijder dubbele distance berekeningen
    # Zoek naar dubbele calculate_distance calls
    content = re.sub(r'distance = self\.calculate_distance\([^)]+\)\s*distance = self\.calculate_distance\([^)]+\)', 
                     'distance = self.calculate_distance(lat, lng, place[\'geometry\'][\'location\'][\'lat\'], place[\'geometry\'][\'location\'][\'lng\'])', 
                     content)
    
    # Schrijf terug
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Bug fix toegepast!")
    print("✓ Test nu opnieuw met een fresh location (niet cached)")

if __name__ == "__main__":
    fix_distance_validation()
