import sqlite3
import requests
from datetime import datetime

def insert_player_data(cursor, player_data):
    """
    Insert new player data into the database, or update if a record for the same day exists.
    """
    cursor.execute('''
        INSERT INTO players (tag, name, total_trophies, timestamp) 
        VALUES (?, ?, ?, DATE('now'))
        ON CONFLICT(tag, timestamp) DO UPDATE SET
        name = excluded.name,
        total_trophies = excluded.total_trophies;
    ''', (player_data['tag'], player_data['name'], player_data['trophies']))



def insert_brawler_data(cursor, player_tag, brawlers_data):
    """
    Insert or replace brawler data for a player into the database.
    """
    for brawler in brawlers_data:
        gadgets = ','.join([gadget['name'] for gadget in brawler.get('gadgets', [])])
        star_powers = ','.join([sp['name'] for sp in brawler.get('starPowers', [])])
        gears = ','.join([gear['name'] for gear in brawler.get('gears', [])])

        cursor.execute('''
            INSERT OR REPLACE INTO brawlers (player_tag, brawler_name, trophies, power_level, gadgets, star_powers, gears, timestamp) 
            VALUES (?, ?, ?, ?, ?, ?, ?, DATE('now'));
        ''', (player_tag, brawler['name'], brawler['trophies'], brawler['power'],
              gadgets, star_powers, gears))


def update_player_data(api_key, player_tag):
    """
    Retrieve player data from the API and update the database.
    """
    url = f'https://api.brawlstars.com/v1/players/%23{player_tag}'
    headers = {'Authorization': f'Bearer {api_key}', 'Accept': 'application/json'}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    player_data = response.json()

    # Connect to the database
    conn = sqlite3.connect('brawlstars_stats.db')
    cursor = conn.cursor()

    # Insert new player and brawler data
    insert_player_data(cursor, player_data)
    insert_brawler_data(cursor, player_tag, player_data['brawlers'])

    # Commit changes and close the database connection
    conn.commit()
    conn.close()

def fetch_and_store_battle_logs(api_key, player_tag, cursor):
    """
    Fetch the battle logs for a player and store them in the database.
    """
    url = f'https://api.brawlstars.com/v1/players/%23{player_tag}/battlelog'
    headers = {'Authorization': f'Bearer {api_key}', 'Accept': 'application/json'}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    battle_logs = response.json()

    for battle in battle_logs['items']:
        battle_time = battle['battleTime']
        event_mode = battle['battle'].get('mode', 'Unknown')
        battle_date = datetime.strptime(battle_time, '%Y%m%dT%H%M%S.%fZ').date()  # Extracting the date from battle_time
        event_id = battle['event'].get('id', 0)
        event_map = battle['event'].get('map', 'Unknown')
        result = battle['battle'].get('result', 'Unknown')
        soloshodown = False

        if event_mode in ['soloShowdown', 'duoShowdown', 'wipeout'] and 'rank' in battle['battle']:
            rank = battle['battle']['rank']
            if event_mode == 'soloShowdown' or event_mode == 'wipeout':
                if rank <=4:
                    result = 'victory'
                elif rank == 5:
                    result = 'draw'
                else:
                    result = 'defeat'
            else:
                if rank <=2:
                    result = 'victory'
                elif rank == 3:
                    result = 'draw'
                else:
                    result = 'defeat'
            if event_mode == 'soloShowdown':
                soloshodown = True

        # Find the player's brawler and trophies in the battle log
        brawler_name, brawler_trophies = find_brawler_in_battle_log(battle, player_tag, soloshodown)

        # Check if the battle log already exists in the database
        cursor.execute('''
            SELECT 1 FROM battle_logs WHERE player_tag = ? AND battle_time = ?
        ''', (player_tag, battle_time))
        exists = cursor.fetchone()

        # If the battle log does not exist, insert it
        if not exists:
            cursor.execute('''
                INSERT INTO battle_logs (player_tag, battle_time, event_mode, event_id, event_map, result, brawler_name, brawler_trophies, battle_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            ''', (player_tag, battle_time, event_mode, event_id, event_map, result, brawler_name, brawler_trophies, battle_date))

def find_brawler_in_battle_log(battle, player_tag, soloshodown=False):
    """
    Find the brawler used by the player in the battle log and return its name and trophies.
    """
    if not soloshodown:
        for team in battle['battle'].get('teams', []):
            for player in team:
                if player['tag'].strip('#') == player_tag:
                    brawler_name = player['brawler']['name']
                    brawler_trophies = player['brawler']['trophies']
                    return brawler_name, brawler_trophies
    else:
        for player in battle['battle'].get('players', []):
            if player['tag'].strip('#') == player_tag:
                brawler_name = player['brawler']['name']
                brawler_trophies = player['brawler']['trophies']
                return brawler_name, brawler_trophies
    print(battle["battle"])
    return 'Unknown', 0  # Default values if the brawler is not found






# Your API key (use a placeholder or environment variable for security)
api_key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImJiNGY0ODdhLTIzZWMtNGE4Ny1iNTJiLWE4MzczYjA3ZmE0YyIsImlhdCI6MTcwNDkwNTUyMywic3ViIjoiZGV2ZWxvcGVyL2U0M2UwMjRhLTBjNzQtYWMyOS03NjI3LTZiNGVjN2NmYTc4NSIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiODYuNzQuMjAwLjEyNiIsIjg3LjEyOS4xNjYuMTg2IiwiMTYyLjI0My4xODQuMjEiLCI2NS4xLjExNi4xNDgiLCIxNjIuMjQ4LjIyNC4xMDMiXSwidHlwZSI6ImNsaWVudCJ9XX0.QDbw3T_G8yFG6wn6IncAcPaW8NTNyht5c9nJ31ryQGRDUPI-rGhr2XxS_hXUwXYNX0_f-eFWDNvNMbL4_hlDTA'

# List of player tags
player_tags = ['YGVJ0VV', 'L8V9LRVV', 'PLUJGG8R2', 'Q8U0GJVG2', '2RQ9R90G9', '8P29PQQR2', '9000JU9V', 'RY0JYYJP9', "RPRLOCURY", "RQ8VC9QRP", "992YU929J", "2QQGOYJJ8", "2PPLYRCJR", "RLYVJ9CPU", "GC9GQJGR"]

# Update data for each player
for tag in player_tags:
    try:
        conn = sqlite3.connect('brawlstars_stats.db')
        cursor = conn.cursor()

        update_player_data(api_key, tag)
        fetch_and_store_battle_logs(api_key, tag, cursor)

        conn.commit()
        conn.close()

        print(f"Data updated for player: {tag}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to update data for player {tag}: {e}")
