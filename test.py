import argparse
import random
import re
from collections import Counter

# Real machine learning classifier (scikit-learn). Falls back to the keyword
# method below if the ML libraries aren't installed.
try:
    import ml_model
    _ML_AVAILABLE = True
except Exception:
    _ML_AVAILABLE = False


EMOTION_LEXICON = {
    "joyful": ["joyful", "ecstatic", "elated", "overjoyed", "pumped", "hyped",
               "blessed", "grateful", "celebrating", "stoked", "buzzing"],
    "joy": ["happy", "joy", "excited", "amazing", "great", "love",
            "wonderful", "awesome", "fantastic", "glad", "delighted", "good",
            "fun", "celebrate", "thrilled", "smile"],
    "sadness": ["sad", "down", "unhappy", "depressed", "cry", "crying", "lonely",
                "heartbroken", "miserable", "gloomy", "hopeless", "tired",
                "exhausted", "drained", "blue"],
    "anger": ["angry", "mad", "furious", "annoyed", "frustrated", "irritated",
              "rage", "hate", "outraged", "upset"],
    "fear": ["afraid", "scared", "anxious", "nervous", "worried", "stressed",
             "terrified", "panic", "uneasy", "tense"],
    "calm": ["calm", "relaxed", "peaceful", "chill", "content", "serene",
             "okay", "fine", "mellow", "easygoing"],
}
NEGATIONS = {"not", "no", "never", "isn't", "wasn't", "don't", "didn't", "can't"}
POSITIVE_EMOTIONS = {"joy", "joyful", "calm"}
NEGATIVE_EMOTIONS = {"sadness", "anger", "fear"}

EMOTION_TO_MOOD = {
    "joyful": "joyful", "joy": "happy", "sadness": "sad", "anger": "energetic",
    "fear": "anxious", "calm": "calm", "neutral": "neutral",
}

# Fallback melodies (note:beats). These only play if a real preview isn't found.
M_RAP = "C5:0.5 D5:0.5 E5:0.5 G5:0.5 E5:0.5 D5:1"
M_HAPPY = "C5:0.5 E5:0.5 G5:0.5 C6:1 G5:0.5 E5:1"
M_SAD = "A4:1 C5:1 E5:1 D5:1 C5:1 A4:2"
M_NEU = "G4:0.5 A4:0.5 C5:1 A4:0.5 G4:0.5 E4:1"
M_CALM = "C5:2 E5:2 G5:1 E5:1"
M_ENERGY = "E5:0.5 E5:0.5 G5:0.5 E5:0.5 A5:0.5 G5:1"
M_ANX = "A4:1 B4:1 C5:1 B4:1 A4:1 G4:2"

SONGS = {
    "joyful": [
        ("Not Like Us", "Kendrick Lamar", "Rap", M_RAP),
        ("Jane!", "The Long Faces", "Rap", M_RAP),
        ("Magnolia", "Playboi Carti", "Rap", M_RAP),
        ("Sky", "Playboi Carti", "Rap", M_RAP),
        ("Stop Breathing", "Playboi Carti", "Rap", M_RAP),
        ("Just Wanna Rock", "Lil Uzi Vert", "Rap", M_RAP),
        ("20 Min", "Lil Uzi Vert", "Rap", M_RAP),
        ("Money So Big", "Yeat", "Rap", M_RAP),
        ("Talk", "Yeat", "Rap", M_RAP),
        ("Rich Minion", "Yeat", "Rap", M_RAP),
        ("Overseas", "Ken Carson", "Rap", M_RAP),
        ("Succubus", "Ken Carson", "Rap", M_RAP),
        ("if looks could kill", "Destroy Lonely", "Rap", M_RAP),
        ("HUMBLE.", "Kendrick Lamar", "Rap", M_RAP),
        ("Money Trees", "Kendrick Lamar", "Rap", M_RAP),
        ("goosebumps", "Travis Scott", "Rap", M_RAP),
        ("SICKO MODE", "Travis Scott", "Rap", M_RAP),
        ("First Class", "Jack Harlow", "Rap", M_RAP),
        ("Drama!", "Nettspend", "Rap", M_RAP),
        ("LIFE IN HELL", "Lancey Foux", "Rap", M_RAP),
    ],
    "happy": [
        ("Happy", "Pharrell Williams", "Pop", M_HAPPY),
        ("September", "Earth, Wind & Fire", "Funk", M_HAPPY),
        ("Dancing Queen", "ABBA", "Disco", M_HAPPY),
        ("Walking on Sunshine", "Katrina & The Waves", "Rock", M_HAPPY),
        ("Mr. Blue Sky", "Electric Light Orchestra", "Rock", M_HAPPY),
        ("Lovely Day", "Bill Withers", "Soul", M_HAPPY),
        ("Three Little Birds", "Bob Marley", "Reggae", M_HAPPY),
        ("Good Vibrations", "The Beach Boys", "Rock", M_HAPPY),
        ("Uptown Funk", "Mark Ronson ft. Bruno Mars", "Funk", M_HAPPY),
        ("24K Magic", "Bruno Mars", "Funk", M_HAPPY),
        ("Can't Stop the Feeling!", "Justin Timberlake", "Pop", M_HAPPY),
        ("I Wanna Dance with Somebody", "Whitney Houston", "Pop", M_HAPPY),
        ("Signed, Sealed, Delivered", "Stevie Wonder", "Soul", M_HAPPY),
        ("I Want You Back", "The Jackson 5", "Soul", M_HAPPY),
        ("Best Day of My Life", "American Authors", "Indie Pop", M_HAPPY),
        ("On Top of the World", "Imagine Dragons", "Pop Rock", M_HAPPY),
        ("Shake It Off", "Taylor Swift", "Pop", M_HAPPY),
        ("Good as Hell", "Lizzo", "Pop", M_HAPPY),
        ("Footloose", "Kenny Loggins", "Rock", M_HAPPY),
        ("Don't Stop Believin'", "Journey", "Rock", M_HAPPY),
    ],
    "sad": [
        ("My Love Mine All Mine", "Mitski", "Indie", M_SAD),
        ("Washing Machine Heart", "Mitski", "Indie", M_SAD),
        ("Motion Sickness", "Phoebe Bridgers", "Indie Folk", M_SAD),
        ("Apocalypse", "Cigarettes After Sex", "Dream Pop", M_SAD),
        ("Sweet", "Cigarettes After Sex", "Dream Pop", M_SAD),
        ("Fade Into You", "Mazzy Star", "Dream Pop", M_SAD),
        ("circle the drain", "Soccer Mommy", "Indie Rock", M_SAD),
        ("we fell in love in october", "girl in red", "Indie", M_SAD),
        ("Self Control", "Frank Ocean", "R&B", M_SAD),
        ("Pink + White", "Frank Ocean", "R&B", M_SAD),
        ("Glimpse of Us", "Joji", "R&B", M_SAD),
        ("SLOW DANCING IN THE DARK", "Joji", "R&B", M_SAD),
        ("Get You", "Daniel Caesar", "R&B", M_SAD),
        ("drunk", "keshi", "R&B", M_SAD),
        ("Romantic Homicide", "d4vd", "Indie", M_SAD),
        ("Here With Me", "d4vd", "Indie", M_SAD),
        ("Lovers Rock", "TV Girl", "Indie Pop", M_SAD),
        ("prom dress", "mxmtoon", "Bedroom Pop", M_SAD),
        ("Kids", "Current Joys", "Indie", M_SAD),
        ("Dead Man Walking", "Brent Faiyaz", "R&B", M_SAD),
    ],
    "energetic": [
        ("My Own Summer (Shove It)", "Deftones", "Alternative Metal", M_ENERGY),
        ("Change (In the House of Flies)", "Deftones", "Alternative Metal", M_ENERGY),
        ("Brianstorm", "Arctic Monkeys", "Indie Rock", M_ENERGY),
        ("R U Mine?", "Arctic Monkeys", "Indie Rock", M_ENERGY),
        ("Head in the Ceiling Fan", "Title Fight", "Punk", M_ENERGY),
        ("Press", "Whirr", "Shoegaze", M_ENERGY),
        ("Cry Baby", "The Neighbourhood", "Alternative", M_ENERGY),
        ("flutter", "Julie", "Shoegaze", M_ENERGY),
    ],
    "calm": [
        ("Tailwhip", "Men I Trust", "Indie Pop", M_CALM),
        ("Numb", "Men I Trust", "Indie Pop", M_CALM),
        ("seasons", "wave to earth", "Indie", M_CALM),
        ("bad", "wave to earth", "Indie", M_CALM),
        ("Valentine", "Laufey", "Jazz Pop", M_CALM),
        ("Best Part", "Daniel Caesar", "R&B", M_CALM),
        ("Cigarettes out the Window", "TV Girl", "Indie Pop", M_CALM),
        ("limbo", "keshi", "R&B", M_CALM),
        ("Only in My Dreams", "The Marías", "Indie Pop", M_CALM),
        ("K.", "Cigarettes After Sex", "Dream Pop", M_CALM),
    ],
    "anxious": [
        ("Your Face", "Wisp", "Shoegaze", M_ANX),
        ("Falling Apart", "Slow Pulp", "Indie Rock", M_ANX),
        ("Jealous", "Eyedress", "Indie", M_ANX),
        ("i walk this earth all by myself", "EKKSTACY", "Indie", M_ANX),
        ("Contingency Song", "Jane Remover", "Digicore", M_ANX),
        ("I Bet on Losing Dogs", "Mitski", "Indie", M_ANX),
        ("Become the Warm Jets", "Current Joys", "Indie", M_ANX),
        ("Scott Street", "Phoebe Bridgers", "Indie Folk", M_ANX),
    ],
    "neutral": [
        ("505", "Arctic Monkeys", "Indie Rock", M_NEU),
        ("Do I Wanna Know?", "Arctic Monkeys", "Indie Rock", M_NEU),
        ("Sweater Weather", "The Neighbourhood", "Alternative", M_NEU),
        ("Daddy Issues", "The Neighbourhood", "Alternative", M_NEU),
        ("Show Me How", "Men I Trust", "Indie Pop", M_NEU),
        ("seasons", "wave to earth", "Indie", M_NEU),
        ("Japanese Denim", "Daniel Caesar", "R&B", M_NEU),
        ("blue", "keshi", "R&B", M_NEU),
        ("Right Side of My Neck", "Faye Webster", "Indie", M_NEU),
        ("Pretty Girl", "Clairo", "Bedroom Pop", M_NEU),
        ("Evergreen", "Omar Apollo", "R&B", M_NEU),
        ("Vampire", "Dominic Fike", "Indie", M_NEU),
        ("Tek It", "Cafuné", "Indie Pop", M_NEU),
        ("Mystery Lady", "Masego", "R&B", M_NEU),
        ("Электрон", "Current Joys", "Indie", M_NEU),
        ("The Less I Know the Better", "Tame Impala", "Psychedelic", M_NEU),
        ("New Person, Same Old Mistakes", "Tame Impala", "Psychedelic", M_NEU),
        ("Space Song", "Beach House", "Dream Pop", M_NEU),
        ("Electric Feel", "MGMT", "Indie", M_NEU),
        ("Sex", "The 1975", "Alternative", M_NEU),
    ],
}


def analyze_keywords(text):
    tokens = re.findall(r"[a-z']+", text.lower())
    hits = Counter()
    for i, word in enumerate(tokens):
        negated = i > 0 and tokens[i - 1] in NEGATIONS
        for emotion, words in EMOTION_LEXICON.items():
            if word in words:
                if negated:
                    flipped = "sadness" if emotion in POSITIVE_EMOTIONS else "joy"
                    hits[flipped] += 1
                else:
                    hits[emotion] += 1

    emotion = hits.most_common(1)[0][0] if hits else "neutral"
    pos = sum(hits[e] for e in POSITIVE_EMOTIONS)
    neg = sum(hits[e] for e in NEGATIVE_EMOTIONS)

    if pos == 0 and neg == 0:
        sentiment = "NEUTRAL"
    elif pos > 0 and neg > 0:
        sentiment = "MIXED"
    elif pos > neg:
        sentiment = "POSITIVE"
    else:
        sentiment = "NEGATIVE"

    return {"sentiment": sentiment, "emotion": emotion, "method": "keywords"}


def analyze(text):
    """Predict emotion + sentiment, using the ML model when available."""
    if _ML_AVAILABLE and text.strip():
        try:
            emotion, confidence = ml_model.predict_emotion(text)
            return {
                "sentiment": ml_model.sentiment_for(emotion),
                "emotion": emotion,
                "method": "ml",
                "confidence": confidence,
            }
        except Exception:
            pass
    return analyze_keywords(text)


def decide_mood(analysis):
    return EMOTION_TO_MOOD.get(analysis["emotion"], "neutral")


# Per-mood queue of not-yet-shown songs, so refreshes cycle through the whole
# list before any song repeats.
_queues = {}


def recommend(mood, limit=5):
    pool = list(SONGS.get(mood, SONGS["neutral"]))
    limit = min(limit, len(pool))
    queue = _queues.get(mood) or []
    # Refill with songs not already queued (avoids duplicates within a batch and
    # repeats across consecutive refreshes) until the pool is exhausted.
    if len(queue) < limit:
        fresh = [s for s in pool if s not in queue]
        random.shuffle(fresh)
        queue = queue + fresh
    result = queue[:limit]
    _queues[mood] = queue[limit:]
    return result


def show(text):
    analysis = analyze(text)
    mood = decide_mood(analysis)

    method = analysis.get("method", "keywords")
    detail = method
    if method == "ml":
        detail = f"ml ({analysis.get('confidence', 0):.0%} confident)"

    print()
    print(f"  Sentiment : {analysis['sentiment']}")
    print(f"  Emotion   : {analysis['emotion']}  [via {detail}]")
    print(f"  Mood      : {mood}")
    print("\n  Songs for you:")
    for i, (title, artist, genre, melody) in enumerate(recommend(mood), 1):
        print(f"    {i}. {title} - {artist} ({genre})")
    print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", "-t")
    args = parser.parse_args()

    if args.text:
        show(args.text)
        return

    print("AI Mood-Based Music Recommender")
    print("Tell me how you're feeling (or type 'quit' to exit).\n")
    while True:
        try:
            text = input("How are you feeling? ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return
        if text.lower() in {"quit", "exit", "q"}:
            print("Goodbye!")
            return
        if text:
            show(text)


if __name__ == "__main__":
    main()
