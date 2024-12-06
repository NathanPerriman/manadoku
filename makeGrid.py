import json
import re
import random

from checkChallenges import meetsChallenge

def scrubText(text):
    # Convert text to lowercase
    text = text.lower()
    # Remove standalone occurrences of "the" using regex with word boundaries
    text = re.sub(r'\bthe\b', '', text)
    # Remove punctuation and whitespace
    text = re.sub(r'[^\w]', '', text)
    return text

chalData = None
validPairs = None
oracleData = None
cardDict = None

def loadData():
    global chalData
    global validPairs
    print("Opening challenge list...")
    with open('mdChallenges.json', 'r') as challenge_file:
        chalData = json.load(challenge_file)
    print("Opening challenge pairs...")
    with open('validPairs.json', 'r') as pairsFile:
        validPairs = json.load(pairsFile)
    print("Opening oracle data...")
    with open('oracle.json', 'r') as oracleFile:
        oracleData = json.load(oracleFile)
    global cardDict
    cardDict = {scrubText(card['name']): card for card in oracleData}

def getFullChallenge(challengeName, challengeChal):
    for challenge in chalData["challenges"]:
        if challenge["name"] == challengeName and challenge["challenge"] == challengeChal:
            return challenge
    return None

def isInvalidColourIdentityPair(chal1, chal2):
    set1 = set(chal1)
    set2 = set(chal2)
    return set1 == set2 or set1.issubset(set2) or set2.issubset(set1)

def pairsFromChallenge(challenge1):
    validChallenges = []
    for pair in validPairs:
        if (pair["category1"] == challenge1["name"] and pair["challenge1"] == challenge1["challenge"]) or \
           (pair["category2"] == challenge1["name"] and pair["challenge2"] == challenge1["challenge"]):
            validChallenges.append(pair)

    if not validChallenges:
        print("NO VALID CHALLENGE PAIRS FOUND WITH "+str(challenge1))
    return validChallenges

def twoChallenges(difficulty):
    try:
        if (difficulty < 1):
            difficulty = 1
    except TypeError:
        print("Invalid Difficulty!")
        quit()

    validChallenges = [
        challenge for challenge in chalData["challenges"]
        if (int(challenge["difficulty"]) == difficulty) or
           (int(challenge["difficulty"]) < difficulty and challenge["progresses"] == "T")
    ]
    if not validChallenges:
        raise ValueError("No valid challenges for difficulty "+str(difficulty))

    challenge1 = random.choice(validChallenges)
    challenge2 = randomPairedChallenge(challenge1, difficulty)
    return challenge1, challenge2

def randomPairedChallenge(challenge1, difficulty, avoid = []):
    validPairs = pairsFromChallenge(challenge1)
    random.shuffle(validPairs)
    for pair in validPairs:
        if pair["category1"] == challenge1["name"] and pair["challenge1"] == challenge1["challenge"]:
            challenge2 = getFullChallenge(pair["category2"], pair["challenge2"])
        else:
            challenge2 = getFullChallenge(pair["category1"], pair["challenge1"])
        if ((int(challenge2["difficulty"]) == difficulty or
            (int(challenge2["difficulty"]) < difficulty and challenge2["progresses"] == "T"))
                and not (challenge2 in avoid)):
            if (challenge1["name"] in ["Colour", "Identity"] and challenge2["name"] in ["Colour", "Identity"]):
                if isInvalidColourIdentityPair(challenge1["challenge"], challenge2["challenge"]):
                    continue
            return challenge2
    raise ValueError("No valid challenge pair found for "+str(challenge1))

def findValidChallengeForMultiple(challenges, difficulty, avoid = []):
    shortList = []
    for candidate in chalData["challenges"]:
        if not ((int(candidate["difficulty"]) == difficulty or
                (int(candidate["difficulty"]) < difficulty and candidate["progresses"] == "T"))):
            continue
        if candidate in avoid:
            continue

        valid = True
        for challenge in challenges:
            if (challenge["name"] in ["Colour", "Identity"] and candidate["name"] in ["Colour", "Identity"]):
                if isInvalidColourIdentityPair(challenge["challenge"], candidate["challenge"]):
                    valid = False
                    break

            validPairFound = any(
                (pair["category1"] == challenge["name"] and pair["challenge1"] == challenge["challenge"] and
                 pair["category2"] == candidate["name"] and pair["challenge2"] == candidate["challenge"]) or
                (pair["category2"] == challenge["name"] and pair["challenge2"] == challenge["challenge"] and
                 pair["category1"] == candidate["name"] and pair["challenge1"] == candidate["challenge"])
                for pair in validPairs
            )
            if not validPairFound:
                valid = False
        if valid:
            shortList.append(candidate)

    if shortList:
        return random.choice(shortList)
    print("NO VALID CHALLENGE FOR "+str(challenges))

def getGrid(difficulty):
    col1, row1 = twoChallenges(difficulty)
    col2 = randomPairedChallenge(row1, difficulty, [col1])
    row2 = findValidChallengeForMultiple([col1, col2], difficulty, [row1])
    col3 = findValidChallengeForMultiple([row1, row2], difficulty, [col1, col2])
    row3 = findValidChallengeForMultiple([col1, col2, col3], difficulty, [row1, row2])

    print("Returning Grid...")
    return [str(difficulty), col1, col2, col3, row1, row2, row3]

def getRandomGrid():
    return getGrid(random.randint(1, 3))

def checkSubmission(userText, rowChallenge, colChallenge):
    userCard = cardDict.get(scrubText(userText))
    if userCard is None:
        print("Cannot find card!")
        return False
    return (meetsChallenge(rowChallenge, userCard) and meetsChallenge(colChallenge, userCard)), userCard["image_uris"]["normal"]

def main():
    loadData()

    [dif, col1, col2, col3, row1, row2, row3] = getRandomGrid()

    print("difficulty: "+str(dif))
    print("col1: " + col1["name"] + ", " + col1["challenge"])
    print("row1: " + row1["name"] + ", " + row1["challenge"])
    print("col2: " + col2["name"] + ", " + col2["challenge"])
    print("row2: " + row2["name"] + ", " + row2["challenge"])
    print("col3: " + col3["name"] + ", " + col3["challenge"])
    print("row3: " + row3["name"] + ", " + row3["challenge"])

if __name__ == "__main__":
    main()