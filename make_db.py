import sqlite3

def create_database():
    # Connect to SQLite database (it will create the file if it does not exist)
    conn = sqlite3.connect('brawlstars_stats.db')

    # Create tables
    cursor = conn.cursor()

    # Table for players
    cursor.execute('''CREATE TABLE IF NOT EXISTS players (
                        tag TEXT,
                        name TEXT,
                        total_trophies INTEGER,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (tag, timestamp)
                     )''')

    # Table for brawlers of each player
    cursor.execute('''CREATE TABLE IF NOT EXISTS brawlers (
                        player_tag TEXT,
                        brawler_name TEXT,
                        trophies INTEGER,
                        power_level INTEGER,
                        gadgets TEXT,
                        star_powers TEXT,
                        gears TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (player_tag, brawler_name, timestamp),
                        FOREIGN KEY(player_tag) REFERENCES players(tag)
                     )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS battle_logs (
    player_tag TEXT,
    battle_time TIMESTAMP,
    event_mode TEXT,
    event_id INTEGER,
    event_map TEXT,
    result TEXT,  -- Win, Lose, Draw, etc.
    brawler_name TEXT,
    brawler_trophies INTEGER,
    battle_date DATE,
    PRIMARY KEY (player_tag, battle_time),
    FOREIGN KEY(player_tag) REFERENCES players(tag)
);
''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
