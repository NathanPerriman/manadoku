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

def pairsFromChallenge(challenge1):
    validChallenges = []
    for pair in validPairs:
        if (pair["category1"] == challenge1["name"] and pair["challenge1"] == challenge1["challenge"]) or \
           (pair["category2"] == challenge1["name"] and pair["challenge2"] == challenge1["challenge"]):
            validChallenges.append(pair)

    if not validChallenges:
        print("NO VALID CHALLENGE PAIRS FOUND WITH "+str(challenge1))
    return validChallenges

def getFullChallenge(challengeName, challengeChal):
    for challenge in chalData["challenges"]:
        if challenge["name"] == challengeName and challenge["challenge"] == challengeChal:
            return challenge
    return None

def randomPairedChallenge(challenge1, difficulty):
    validPairs = pairsFromChallenge(challenge1)
    while True:
        pair = random.choice(validPairs)
        if pair["category1"] == challenge1["name"] and pair["challenge1"] == challenge1["challenge"]:
            challenge2 = getFullChallenge(pair["category2"], pair["challenge2"])
            if int(challenge2["difficulty"]) == difficulty or (
                    int(challenge2["difficulty"]) < difficulty and challenge2["progresses"] == "T"):
                break
        else:
            challenge2 = getFullChallenge(pair["category1"], pair["challenge1"])
            if int(challenge2["difficulty"]) == difficulty or (
                    int(challenge2["difficulty"]) < difficulty and challenge2["progresses"] == "T"):
                break
    return challenge2

def twoChallenges(difficulty):
    try:
        if (difficulty < 1):
            difficulty = 1
    except TypeError:
        print("Invalid Difficulty!")
        quit()

    challenge1 = None
    challenge2 = None
    while True:
        challenge1 = random.choice(chalData["challenges"])
        if (int(challenge1["difficulty"]) == difficulty) or (
                int(challenge1["difficulty"]) < difficulty and challenge1["progresses"] == "T"):
            break

    challenge2 = randomPairedChallenge(challenge1, difficulty)

    #print("Difficulty " + str(difficulty) + ": \'"+challenge1["name"]+", "+challenge1["challenge"]+"\' + \'"+challenge2["name"]+", "+challenge2["challenge"]+"\'")
    return challenge1, challenge2

def findValidChallengeForMultiple(challenges, difficulty):
    shortList = []
    for candidate in chalData["challenges"]:
        if not ((int(candidate["difficulty"]) == difficulty or
                (int(candidate["difficulty"]) < difficulty and candidate["progresses"] == "T"))):
            continue
        valid = True
        for challenge in challenges:
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
    col2 = randomPairedChallenge(row1, difficulty)
    row2 = findValidChallengeForMultiple([col1, col2], difficulty)
    col3 = findValidChallengeForMultiple([row1, row2], difficulty)
    row3 = findValidChallengeForMultiple([col1, col2, col3], difficulty)

    print("Returning Grid...")
    return [str(difficulty), col1, col2, col3, row1, row2, row3]

def getRandomGrid():
    return getGrid(random.randint(1, 3))

def checkSubmission(userText, rowChallenge, colChallenge):
    userCard = cardDict.get(scrubText(userText))
    if userCard is None:
        print("Cannot find card!")
        return False
    return meetsChallenge(rowChallenge, userCard) and meetsChallenge(colChallenge, userCard)

def main():
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