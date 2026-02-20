import sqlite3
import json
import os

# Create simple database with test data for COTS search
conn = sqlite3.connect('parts.db')
cursor = conn.cursor()

# Create table matching the ORM model
cursor.execute('''
CREATE TABLE IF NOT EXISTS cots_items (
    part_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_cost REAL,
    weight_g REAL,
    metadata_dict TEXT
)
''')

# Insert test data including M3 screw
test_data = [
    {
        'part_id': 'M3-16-SS',
        'name': 'M3 x 16mm Stainless Steel Screw',
        'category': 'fastener',
        'unit_cost': 0.15,
        'weight_g': 1.2,
        'metadata_dict': json.dumps({
            'manufacturer': 'Generic',
            'material': 'stainless_steel',
            'size': 'M3x16'
        })
    },
    {
        'part_id': 'M3-NUT-SS',
        'name': 'M3 Stainless Steel Nut',
        'category': 'fastener', 
        'unit_cost': 0.05,
        'weight_g': 0.8,
        'metadata_dict': json.dumps({
            'manufacturer': 'Generic',
            'material': 'stainless_steel',
            'size': 'M3'
        })
    },
    {
        'part_id': 'BEARING-608',
        'name': '608 Ball Bearing',
        'category': 'bearing',
        'unit_cost': 2.50,
        'weight_g': 8.5,
        'metadata_dict': json.dumps({
            'manufacturer': 'Generic',
            'size': '608'
        })
    }
]

for item in test_data:
    cursor.execute('''
INSERT OR REPLACE INTO cots_items (part_id, name, category, unit_cost, weight_g, metadata_dict)
VALUES (?, ?, ?, ?, ?, ?)
''', (item['part_id'], item['name'], item['category'], item['unit_cost'], item['weight_g'], item['metadata_dict']))

conn.commit()
conn.close()

print('✅ Created parts.db with test COTS data')
if os.path.exists('parts.db'):
    print('Database size:', os.path.getsize('parts.db'), 'bytes')
else:
    print('❌ Database not created')
