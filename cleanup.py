import sqlite3
from datetime import datetime

# Connect to the SQLite database
conn = sqlite3.connect('brawlstars_stats.db')
cursor = conn.cursor()

# Set the cutoff date for cleaning up old entries
cutoff_date = '2024-03-29'

# Remove old entries from the players table
cursor.execute('DELETE FROM players WHERE date(timestamp) <= ?', (cutoff_date,))

# Remove old entries from the brawlers table
cursor.execute('DELETE FROM brawlers WHERE date(timestamp) <= ?', (cutoff_date,))

# Remove old entries from the battle_logs table
cursor.execute('DELETE FROM battle_logs WHERE date(battle_date) <= ?', (cutoff_date,))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Old entries removed successfully.")