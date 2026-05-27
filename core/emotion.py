def detect_emotion(text):
    text = text.lower()

    if any(w in text for w in ["sad", "tired", "upset", "depressed", "lonely"]):
        return "sad"
    if any(w in text for w in ["happy", "excited", "great", "awesome", "love"]):
        return "happy"
    if any(w in text for w in ["stress", "pressure", "overwhelmed", "anxious", "worried"]):
        return "stressed"
    if any(w in text for w in ["angry", "frustrated", "annoyed", "mad", "furious"]):
        return "angry"
    if any(w in text for w in ["confused", "lost", "don't understand", "what do you mean"]):
        return "confused"

    return "neutral"