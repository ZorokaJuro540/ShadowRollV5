"""
Clean database.py file - Remove all custom characters section and duplicates
Keep only the base characters list without duplication
"""

def clean_database_file():
    """Remove custom characters section and clean up database.py"""
    
    # Read the current file
    with open("core/database.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find the end of the base characters list (before custom section)
    base_end_marker = '            ("Akane Kurokawa", "Oshi no Ko", "Secret", 150000,'
    
    # Find where the custom section starts
    custom_start_marker = "# Tous les personnages sont maintenant gérés via les commandes admin"
    
    # Find where the character extending happens
    extend_marker = "characters.extend(custom_characters)"
    
    # Get the position of these markers
    base_end_pos = content.find(base_end_marker)
    custom_start_pos = content.find(custom_start_marker)
    extend_pos = content.find(extend_marker)
    
    if base_end_pos == -1 or custom_start_pos == -1:
        print("❌ Could not find required markers in database.py")
        return
    
    # Find the end of the Akane Kurokawa entry
    akane_end = content.find("),", base_end_pos) + 2
    
    # Find the start of the track synchronized characters section
    track_start = content.find("# Track synchronized characters for logging")
    
    if track_start == -1:
        print("❌ Could not find tracking section")
        return
    
    # Build the new content
    new_content = (
        content[:akane_end] + "\n        ]\n\n        " +
        "# Tous les personnages sont maintenant gérés via les commandes admin\n        " +
        "# Utilisez !createchar ou le panneau admin (!admin) pour ajouter des personnages\n        " +
        "# Plus de section custom_characters pour éviter les doublons\n\n        " +
        content[track_start:]
    )
    
    # Write the cleaned file
    with open("core/database.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("✅ Database file cleaned successfully!")
    print("✅ Removed all custom characters section")
    print("✅ No more duplicate character definitions")

if __name__ == "__main__":
    clean_database_file()