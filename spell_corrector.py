from rapidfuzz import process, fuzz

def build_vocabulary(metadata):
    """
    Build vocabulary from dataset titles only (not content).
    Titles are cleaner and more meaningful.
    """
    vocab = set()
    for chunk in metadata:
        words = chunk['title'].lower().split()
        for word in words:
            if len(word) > 3:
                vocab.add(word)
    return list(vocab)

def correct_spelling(text, vocabulary, threshold=85):
    """
    Correct spelling using fuzzy matching against dataset vocabulary.
    Only corrects words with very high similarity score.
    """
    words = text.split()
    corrected_words = []
    
    for word in words:
        if len(word) > 4:
            match = process.extractOne(
                word.lower(), 
                vocabulary, 
                scorer=fuzz.ratio,
                score_cutoff=threshold
            )
            if match and match[0] != word.lower():
                print(f"Spell corrected: '{word}' -> '{match[0]}'")
                corrected_words.append(match[0])
            else:
                corrected_words.append(word)
        else:
            corrected_words.append(word)
    
    return " ".join(corrected_words)