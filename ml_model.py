"""Machine learning mood classifier.

Real ML pipeline (scikit-learn):
  - Feature extraction: TF-IDF over word/bigram tokens
  - Model: Logistic Regression (multiclass)
  - Trained on a labeled dataset of mood phrases, then used to predict the
    emotion of new text.

The trained pipeline is cached to disk (mood_model.joblib) so it trains once.
"""

import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

try:
    import joblib
except Exception:  # pragma: no cover
    joblib = None

MODEL_PATH = os.path.join(os.path.dirname(__file__), "mood_model.joblib")

# Labeled training data: (text, emotion). Emotions match EMOTION_TO_MOOD in test.py.
TRAINING_DATA = [
    # joyful (celebratory / hyped)
    ("i feel ecstatic and on top of the world", "joyful"),
    ("this is the best day ever i am so pumped", "joyful"),
    ("i am overjoyed and celebrating tonight", "joyful"),
    ("feeling blessed grateful and hyped up", "joyful"),
    ("i am buzzing with energy lets party", "joyful"),
    ("absolutely thrilled and stoked right now", "joyful"),
    ("i am elated everything is amazing today", "joyful"),
    ("so hyped i could dance all night", "joyful"),
    # joy (happy / content positive)
    ("i am so happy and excited today was amazing", "joy"),
    ("what a wonderful and great day i feel good", "joy"),
    ("i feel delighted and cheerful this morning", "joy"),
    ("having so much fun i love this", "joy"),
    ("i am glad and smiling feeling fantastic", "joy"),
    ("this makes me really happy and joyful", "joy"),
    ("feeling positive and bright today", "joy"),
    ("i am content and pleased with everything", "joy"),
    # sadness
    ("i feel so sad and lonely right now", "sadness"),
    ("i am heartbroken and want to cry", "sadness"),
    ("everything feels gloomy and hopeless", "sadness"),
    ("i am exhausted drained and feeling blue", "sadness"),
    ("i feel down depressed and miserable", "sadness"),
    ("i am tired and unhappy today", "sadness"),
    ("my heart hurts and i feel empty", "sadness"),
    ("i feel like crying and everything is dark", "sadness"),
    # anger
    ("i am so angry and furious right now", "anger"),
    ("this makes me mad and frustrated", "anger"),
    ("i am irritated annoyed and full of rage", "anger"),
    ("i hate this i am so upset", "anger"),
    ("feeling outraged and ready to explode", "anger"),
    ("i am fed up and really frustrated", "anger"),
    ("everything is making me furious today", "anger"),
    ("i am annoyed and cannot stand this", "anger"),
    # fear / anxious
    ("i feel anxious and worried about everything", "fear"),
    ("i am so nervous and scared right now", "fear"),
    ("i feel stressed and tense about the future", "fear"),
    ("i am terrified and full of panic", "fear"),
    ("feeling uneasy and afraid today", "fear"),
    ("i am overwhelmed and anxious about work", "fear"),
    ("my mind is racing with worry and fear", "fear"),
    ("i feel on edge and really nervous", "fear"),
    # calm
    ("i feel calm relaxed and peaceful", "calm"),
    ("everything is chill and serene right now", "calm"),
    ("i am content mellow and at ease", "calm"),
    ("feeling relaxed and easygoing today", "calm"),
    ("i am peaceful and calm this evening", "calm"),
    ("just feeling okay and laid back", "calm"),
    ("i feel quiet and tranquil right now", "calm"),
    ("a soft and gentle peaceful mood", "calm"),
    # neutral
    ("i am just having a normal day", "neutral"),
    ("nothing special going on right now", "neutral"),
    ("i feel okay just an average day", "neutral"),
    ("not much happening today", "neutral"),
    ("it is a regular ordinary afternoon", "neutral"),
    ("i feel fine nothing in particular", "neutral"),
    ("just sitting around doing some stuff", "neutral"),
    ("a plain and uneventful day so far", "neutral"),
]

POSITIVE_EMOTIONS = {"joy", "joyful", "calm"}
NEGATIVE_EMOTIONS = {"sadness", "anger", "fear"}

_pipeline = None


def train():
    """Train the TF-IDF + Logistic Regression pipeline and save it."""
    texts = [t for t, _ in TRAINING_DATA]
    labels = [y for _, y in TRAINING_DATA]
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
        ("clf", LogisticRegression(max_iter=1000)),
    ])
    pipe.fit(texts, labels)
    if joblib is not None:
        joblib.dump(pipe, MODEL_PATH)
    return pipe


def _get_pipeline():
    global _pipeline
    if _pipeline is not None:
        return _pipeline
    if joblib is not None and os.path.exists(MODEL_PATH):
        _pipeline = joblib.load(MODEL_PATH)
    else:
        _pipeline = train()
    return _pipeline


def predict_emotion(text):
    """Predict an emotion and a confidence for the given text."""
    pipe = _get_pipeline()
    emotion = pipe.predict([text])[0]
    confidence = float(max(pipe.predict_proba([text])[0]))
    return emotion, confidence


def sentiment_for(emotion):
    if emotion in POSITIVE_EMOTIONS:
        return "POSITIVE"
    if emotion in NEGATIVE_EMOTIONS:
        return "NEGATIVE"
    return "NEUTRAL"


if __name__ == "__main__":
    train()
    for sample in ["i am so happy and excited",
                   "i feel sad and lonely",
                   "i am furious and annoyed",
                   "i feel ecstatic and pumped",
                   "just a normal day"]:
        emo, conf = predict_emotion(sample)
        print(f"{sample!r:45} -> {emo} ({conf:.0%})")
