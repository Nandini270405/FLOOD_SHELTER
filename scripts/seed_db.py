# Creates and fills the extended shelter database for flood

import sqlite3

conn = sqlite3.connect('shelter.db')
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS app_metadata")
c.execute("DROP TABLE IF EXISTS shelters")

c.execute("""
    CREATE TABLE shelters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        capacity INTEGER,
        available_beds INTEGER,
        distance REAL,
        accessibility TEXT,
        elevation_level TEXT,
        proximity_to_water TEXT,
        medical_facility TEXT,
        latitude REAL,
        longitude REAL
    )
""")

c.execute("""
    CREATE TABLE app_metadata (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
""")

shelters_data = [
    ('Shelter A', 100, 30, 2.5, 'easy',     'high',   'moderate', 'advanced', 20.3068, 85.8199),
    ('Shelter B', 80, 5, 5.0, 'moderate',   'medium', 'very close', 'basic', 20.3130, 85.8254),
    ('Shelter C', 60, 10, 1.0, 'difficult', 'low',    'very close', 'none', 20.3002, 85.8107),
    ('Shelter D', 120, 50, 3.0, 'easy',     'high',   'far',        'advanced', 20.3218, 85.8342),
    ('Shelter E', 90, 20, 6.5, 'moderate',  'medium', 'moderate',   'basic', 20.2976, 85.8441),
    ('Shelter F', 70, 0, 4.5, 'difficult',  'low',    'very close', 'none', 20.2929, 85.8215),
    ('Shelter G', 85, 15, 2.0, 'moderate',  'medium', 'moderate',   'basic', 20.3155, 85.8094),
    ('Shelter H', 110, 40, 3.8, 'easy',     'high',   'far',        'advanced', 20.3266, 85.8178),
    ('Shelter I', 95, 25, 7.0, 'difficult', 'medium', 'far',        'basic', 20.2888, 85.8352),
    ('Shelter J', 75, 18, 1.5, 'moderate',  'medium', 'moderate',   'basic', 20.3092, 85.8039),
    ('Shelter K', 65, 22, 2.2, 'easy',      'medium', 'moderate',   'basic', 20.3188, 85.8421),
    ('Shelter L', 55, 5, 6.2, 'difficult',  'low',    'very close', 'none', 20.2844, 85.8132),
    ('Shelter M', 105, 35, 4.0, 'moderate', 'high',   'moderate',   'advanced', 20.3290, 85.8280),
    ('Shelter N', 60, 8, 8.0, 'moderate',   'medium', 'far',        'basic', 20.2795, 85.8233),
    ('Shelter O', 130, 60, 3.5, 'easy',     'high',   'far',        'advanced', 20.3336, 85.8099),
    ('Shelter P', 40, 15, 9.0, 'difficult', 'low',    'very close', 'none', 20.2738, 85.8380),
    ('Shelter Q', 90, 25, 5.5, 'moderate',  'medium', 'moderate',   'basic', 20.3057, 85.8515),
    ('Shelter R', 100, 30, 1.8, 'easy',     'high',   'moderate',   'advanced', 20.3199, 85.7970),
    ('Shelter S', 80, 12, 4.8, 'moderate',  'medium', 'very close', 'basic', 20.2951, 85.8541),
    ('Shelter T', 95, 27, 6.0, 'difficult', 'medium', 'far',        'basic', 20.2866, 85.8015),
    ('Shelter U', 50, 50, 10.0, 'easy',     'medium', 'far',        'none', 20.2716, 85.8158),
    ('Shelter V', 120, 5, 0.5, 'difficult', 'low',    'very close', 'none', 20.3385, 85.8209),
    ('Shelter W', 75, 18, 7.2, 'moderate',  'low',    'moderate',   'basic', 20.2762, 85.8460),
    ('Shelter X', 90, 20, 3.3, 'easy',      'high',   'moderate',   'advanced', 20.3241, 85.8476),
    ('Shelter Y', 110, 0, 5.5, 'moderate',  'medium', 'far',        'none', 20.3014, 85.7922),
    ('Shelter Z', 60, 40, 2.0, 'difficult', 'medium', 'moderate',   'basic', 20.3125, 85.8368),
]

c.executemany("""
    INSERT INTO shelters 
    (name, capacity, available_beds, distance, accessibility, elevation_level, proximity_to_water, medical_facility, latitude, longitude)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", shelters_data)

c.executemany(
    "INSERT INTO app_metadata (key, value) VALUES (?, ?)",
    [
        ("source_type", "demo"),
        ("dataset_name", "Built-in demo shelters"),
    ],
)

conn.commit()
conn.close()

print("Done")


