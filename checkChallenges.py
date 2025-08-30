import json
import re
from collections import Counter
import random


def meetsChallenge(challenge, entry):
    success = False

    # print("Checking if entry "+entry["name"]+" meets challenge \'"+challenge["name"]+": "+challengeGoal+"\'...")

    if challenge["compare"] in entry:
        challengeGoal = challenge["challenge"]
        entryComp = entry[challenge["compare"]]

        if challenge["name"] == "Type" or challenge["name"] == "Keyword":
            success = challengeGoal in entryComp

        elif challenge["name"] == "Colour" or challenge["name"] == "Identity":
            if challengeGoal == "Colourless":
                success = not entryComp
            elif challengeGoal == "Multicolour":
                success = (len(entryComp) >= 2)
            else:
                submission_string = ''.join(entryComp)
                success = Counter(submission_string) == Counter(challengeGoal)

        elif challenge["name"] == "Mana Cost":
            if challengeGoal == "{X}" or challengeGoal == "{X}{X}":
                success = challengeGoal in entryComp
            elif challengeGoal == "Phyrexian":
                success = "/P" in entryComp
            elif challengeGoal == "Split":
                match = re.search(r"[WUBRG2]/[WUBRG2]", entryComp)
                success = match is not None

        elif challenge["name"] == "Converted Mana Cost":
            trueSub = str(entryComp).split('.')[0]
            if challengeGoal.isdigit():
                success = challenge["challenge"] == trueSub
            elif ',' in challengeGoal:
                success = trueSub in challenge["challenge"]
            elif challengeGoal.endswith('+') and challengeGoal[:-1].isdigit():
                minimum = int(challengeGoal[:-1])
                success = trueSub.isdigit() and int(trueSub) >= minimum

        elif challenge["name"] == "Produced Mana":
            if challengeGoal == "Coloured":
                success = any(letter != "C" for letter in entryComp)
            elif challengeGoal == "Colourless":
                success = any(letter == "C" for letter in entryComp)
            else:
                challenge_letters = set(re.findall(r"[A-Z]", challengeGoal.upper()))
                entry_letters = set(re.findall(r"[A-Z]", str(entryComp).upper()))
                success = challenge_letters == entry_letters

        elif challenge["name"] == "Format Legalities":
            keywords = ["commander", "modern", "standard", "pauper"]

            for keyword in keywords:
                if keyword in challengeGoal.lower():
                    if keyword == "standard":
                        success = entryComp.get("standard") == "legal"
                    else:
                        success = entryComp.get(keyword) == "banned"

        elif challenge["name"] == "Power" or challenge["name"] == "Toughness":
            if entryComp == "*":
                success = challengeGoal == "*"
            elif challengeGoal.isdigit():
                success = challengeGoal == entryComp
            elif ',' in challengeGoal:
                success = entryComp in challengeGoal
            elif challengeGoal.endswith('+') and challengeGoal[:-1].isdigit():
                minimum = int(challengeGoal[:-1])
                success = entryComp.isdigit() and int(entryComp) >= minimum

    return success
