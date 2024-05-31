import sqlite3
import csv
from collections import defaultdict

import sqlite3
import csv
from collections import defaultdict

def query_and_export_trophy_data():
    conn = sqlite3.connect('brawlstars_stats.db')
    cursor = conn.cursor()

    # Query the database for total trophies per player per day
    cursor.execute('''
        SELECT tag, name, total_trophies, DATE(timestamp)
        FROM players
        ORDER BY tag, DATE(timestamp)
    ''')
    rows = cursor.fetchall()
    conn.close()

    # Process the data
    player_data = defaultdict(lambda: {'name': '', 'trophies': defaultdict(int)})
    dates = set()
    for tag, name, trophies, date in rows:
        player_data[tag]['name'] = name
        player_data[tag]['trophies'][date] = trophies
        dates.add(date)

    # Sort the dates
    sorted_dates = sorted(dates)

    # Export to a single CSV file
    with open('players_trophies_over_time.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['tag', 'name'] + sorted_dates)
        for tag, data in player_data.items():
            row = [tag, data['name']] + [data['trophies'][date] for date in sorted_dates]
            writer.writerow(row)

# Run the function
query_and_export_trophy_data()

import sqlite3
import csv
from collections import defaultdict

def build_tag_name_mapping(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT tag, name FROM players')
    d = {}
    for tag, name in cursor.fetchall():
        d[tag[1:]] = name
    return d

def query_and_export_brawler_data():
    conn = sqlite3.connect('brawlstars_stats.db')

    # Create a tag-to-name mapping
    tag_name_mapping = build_tag_name_mapping(conn)

    cursor = conn.cursor()

    # Query the database for brawler trophies per player per day
    cursor.execute('''
        SELECT player_tag, brawler_name, trophies, DATE(timestamp)
        FROM brawlers
        ORDER BY player_tag, brawler_name, DATE(timestamp)
    ''')
    rows = cursor.fetchall()
    conn.close()

    # Process the data
    brawler_data = defaultdict(lambda: defaultdict(lambda: {'trophies': defaultdict(int)}))
    dates = set()
    for player_tag, brawler_name, trophies, date in rows:
        brawler_data[player_tag][brawler_name]['trophies'][date] = trophies
        dates.add(date)

    # Sort the dates
    sorted_dates = sorted(dates)

    # Export to a single CSV file
    with open('brawlers_trophies_over_time.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['player_tag', 'player_name', 'brawler_name'] + sorted_dates)
        for player_tag, brawlers in brawler_data.items():
            player_name = tag_name_mapping.get(player_tag, 'Unknown')
            for brawler_name, data in brawlers.items():
                row = [player_tag, player_name, brawler_name] + [data['trophies'][date] for date in sorted_dates]
                writer.writerow(row)

# Run the function
query_and_export_brawler_data()

def query_and_export_battlelog_data():
    conn = sqlite3.connect('brawlstars_stats.db')

    # Create a tag-to-name mapping
    tag_name_mapping = build_tag_name_mapping(conn)

    cursor = conn.cursor()

    # Query the database for brawler trophies per player per day
    cursor.execute('''
        SELECT player_tag, brawler_name, event_mode, event_map, result, brawler_trophies, DATE(battle_date)
        FROM brawlers
        ORDER BY player_tag, brawler_name, event_mode, event_map, DATE(timestamp)
    ''')
    rows = cursor.fetchall()
    conn.close()

    # Process the data
    brawler_data = defaultdict(lambda: defaultdict(lambda: {'trophies': defaultdict(int)}))
    dates = set()
    for player_tag, brawler_name, trophies, date in rows:
        brawler_data[player_tag][brawler_name]['trophies'][date] = trophies
        dates.add(date)

    # Sort the dates
    sorted_dates = sorted(dates)

    # Export to a single CSV file
    with open('brawlers_trophies_over_time.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['player_tag', 'player_name', 'brawler_name'] + sorted_dates)
        for player_tag, brawlers in brawler_data.items():
            player_name = tag_name_mapping.get(player_tag, 'Unknown')
            for brawler_name, data in brawlers.items():
                row = [player_tag, player_name, brawler_name] + [data['trophies'][date] for date in sorted_dates]
                writer.writerow(row)

# Run the function
query_and_export_brawler_data()


def query_and_export_battlelog_data():
    # Connect to the database
    conn = sqlite3.connect('brawlstars_stats.db')

    # Create a tag-to-name mapping
    tag_name_mapping = build_tag_name_mapping(conn)

    cursor = conn.cursor()

    # Query the database for battle logs per player, excluding specified players
    cursor.execute('''
        SELECT player_tag, battle_time, event_mode, event_map, result, brawler_name, brawler_trophies, battle_date
        FROM battle_logs
        WHERE player_tag NOT IN ('2ULL2VUUQ', 'YJ9G2RPUL')
        ORDER BY player_tag, brawler_name, event_mode, event_map
    ''')
    rows = cursor.fetchall()

    conn.close()

    # Export to a single CSV file
    with open('filtered_battlelogs.csv', 'w', newline='') as file:
        writer = csv.writer(file)

        # Write the header row
        writer.writerow(
            ['player_name', 'battle_time', 'event_mode', 'event_map', 'result', 'brawler_name', 'brawler_trophies',
             'battle_date'])

        for row in rows:
            # Replace the player_tag with the player name
            player_tag, battle_time, event_mode, event_map, result, brawler_name, brawler_trophies, battle_date = row

            player_name = tag_name_mapping.get(player_tag, 'Unknown')
            print()
            writer.writerow(
                [player_name, battle_time, event_mode, event_map, result, brawler_name, brawler_trophies, battle_date])


# Run the function
query_and_export_battlelog_data()
