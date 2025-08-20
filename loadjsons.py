import json
import requests
import os
import itertools
from checkChallenges import meetsChallenge
from datetime import datetime

# API URLs for 'oracle' and 'full' JSON files
ORACLE_API_URL = "https://api.scryfall.com/bulk-data/oracle-cards"
FULL_API_URL = "https://api.scryfall.com/bulk-data/default-cards"

downloadNew = True
updateOracle = True
updatePairs = True

oracleData = None


def download_json(url, filename):
    """
    Download JSON data by first retrieving a 'download_uri' from the initial URL,
    then making a second request to download the JSON data and save it to a local file.
    """
    # Step 1: Make the initial request to get the 'download_uri'
    response = requests.get(url)
    response.raise_for_status()  # Raise an error if the request failed
    initial_data = response.json()

    # Ensure 'download_uri' exists in the response
    if 'download_uri' not in initial_data:
        raise ValueError("The response does not contain 'download_uri' field.")

    # Step 2: Use the 'download_uri' to make the second request for the actual JSON data
    download_url = initial_data['download_uri']
    data_response = requests.get(download_url)
    data_response.raise_for_status()  # Raise an error if the request failed
    data = data_response.json()

    # Step 3: Save the final JSON data to the specified file
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Data successfully downloaded and saved to {filename}")


def update_oracle_with_first_set_and_sets_list(oracle_path, full_path):
    """Add 'first_set' and 'sets_list' fields to each card in the 'oracle' JSON data."""
    global oracleData

    print("Loading full list JSON...")
    # Load 'full' JSON data for reference
    with open(full_path, 'r') as full_file:
        full_data = json.load(full_file)

    # Filter out cards without 'oracle_id' in full_data
    full_data = [card for card in full_data if 'oracle_id' in card]

    print("Gathering all sets per card in full list...")
    # Create a dictionary to track 'first_set' and 'sets_list' for each card by oracle_id
    card_info = {}
    for card in full_data:
        card_id = card['oracle_id']
        card_set = card['set']

        # If the card ID is not already in the dictionary, initialize its entry
        if card_id not in card_info:
            card_info[card_id] = {
                'first_set': card_set if not card['reprint'] else None,
                'sets_list': []
            }

        # Add this set to the 'sets_list' for this card ID
        card_info[card_id]['sets_list'].append(card_set)

        # Update 'first_set' if this is the first printing (non-reprint) of the card
        if not card['reprint'] and not card_info[card_id]['first_set']:
            card_info[card_id]['first_set'] = card_set

    print("Loading oracle JSON for editing...")
    # Load 'oracle' JSON data for editing
    with open(oracle_path, 'r') as oracle_file:
        oracle_data = json.load(oracle_file)

    # Filter out unwanted cards based on 'type_line' and 'set_name'
    oracle_data = [
        card for card in oracle_data
        if 'oracle_id' in card and not (
                "Card" in card.get('type_line', '') or
                "Token" in card.get('type_line', '') or
                card.get('type_line') in {"Stickers", "Vanguard"} or
                card.get('set_name') == "Unknown Event"
        )
    ]

    print("Removing unnecessary fields...")
    # Define the fields to be removed
    fields_to_remove = {
        "mtgo_id", "mtgo_foil_id", "prices", "related_uris",
        "edhrec_rank", "story_spotlight", "full_art", "textless",
        "set_search_uri", "prints_search_uri", "lang", "games",
        "reserved", "foil", "nonfoil", "finishes", "oversized",
        "reprint", "set_id", "rulings_uri", "digital", "flavor_text",
        "set_type", "set_uri", "scryfall_set_uri", "card_back_id",
        "artist", "illustration_id", "border_color", "frame", "booster",
        "tcgplayer_id", "cardmarket_id", "layout", "highres_image",
        "image_status", "promo", "variation", "set", "set_name",
        "artist_ids", "multiverse_ids", "released_at", "security_stamp",
        "preview", "penny_rank", "arena_id", "pomo_types", "collector_number",
        "watermark", "frame_effects", "all_parts"
    }
    legalities_to_remove = {
        "future", "historic", "timeless", "gladiator", "pioneer",
        "explorer", "legacy", "vintage", "penny", "oathbreaker",
        "standardbrawl", "brawl", "alchemy", "paupercommander",
        "duel", "oldschool", "premodern", "predh"
    }
    for card in oracle_data:
        for field in fields_to_remove:
            card.pop(field, None)  # Remove the field if it exists, ignore if not
        if "legalities" in card:
            for key in legalities_to_remove:
                card["legalities"].pop(key, None)

    print("Updating oracle JSON with sets data...")
    # Update each card in 'oracle' with "first_set" and "sets_list"
    for card in oracle_data:
        card_id = card['oracle_id']

        # Retrieve 'first_set' and 'sets_list' from card_info
        if card_id in card_info:
            card['first_set'] = card_info[card_id]['first_set']
            card['sets_list'] = list(set(card_info[card_id]['sets_list']))

    oracleData = oracle_data

    print("Saving updates...")
    # Save the updated 'oracle' JSON data
    with open(oracle_path, 'w') as oracle_file:
        json.dump(oracle_data, oracle_file, indent=4)

    print("oracle.json updated with 'first_set' and 'sets_list' for each card.")


def saveValidPairs(challengesPath, pairsPath):
    print("Opening challenges JSON...")
    with open(challengesPath, 'r') as challengeFile:
        challengeData = json.load(challengeFile)

    challenges_by_name = {}
    for challenge in challengeData["challenges"]:
        challenges_by_name.setdefault(challenge["name"], []).append(challenge)

    print("Finding valid challenge pairs...")
    validPairs = []
    for category1, category2 in itertools.combinations_with_replacement(challenges_by_name.keys(), 2):
        for challenge1 in challenges_by_name[category1]:
            for challenge2 in challenges_by_name[category2]:
                if category1 == category2 and challenge1["challenge"] == challenge2["challenge"]:
                    continue

                validName = None
                for obj in oracleData:
                    if meetsChallenge(challenge1, obj) and meetsChallenge(challenge2, obj):
                        validName = obj.get("name")
                        break
                if validName:
                    validPairs.append({
                        "category1": category1,
                        "challenge1": challenge1["challenge"],
                        "category2": category2,
                        "challenge2": challenge2["challenge"],
                        "proof": validName
                    })

    print("Saving valid pairs JSON...")
    with open(pairsPath, "w") as valid_pairs_file:
        json.dump(validPairs, valid_pairs_file, indent=4)


def main():
    # Define paths for local JSON files
    oracle_path = 'oracle.json'
    full_path = 'full.json'
    challenges_path = 'mdChallenges.json'
    pairs_path = 'validPairs.json'

    if (downloadNew):
        # Download the latest data
        print("Downloading oracle JSON...")
        download_json(ORACLE_API_URL, oracle_path)
        print("Downloading full JSON...")
        download_json(FULL_API_URL, full_path)

    if (updateOracle):
        update_oracle_with_first_set_and_sets_list(oracle_path, full_path)

    if (updatePairs):
        if (not updateOracle):
            global oracleData
            with open(oracle_path) as oracle_file:
                oracleData = json.load(oracle_file)
        saveValidPairs(challenges_path, pairs_path)


if __name__ == "__main__":
    main()
