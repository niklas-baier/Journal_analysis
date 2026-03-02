# contains the multi-language error correction with word lists
import pandas as pd
import nltk
import re
import os
import urllib.request
from nltk.tokenize import word_tokenize, sent_tokenize
from langdetect import detect, detect_langs, DetectorFactory


# --- Smart German Umlaut Preprocessing ---

def download_german_wordlist(url='https://raw.githubusercontent.com/davidak/wortliste/master/wortliste.txt', 
                              filepath='german_words.txt'):
    if os.path.exists(filepath): return filepath
    try:
        urllib.request.urlretrieve(url, filepath)
        return filepath
    except Exception: return None

def load_german_wordlist(filepath='german_words.txt'):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        return {'straße', 'müssen', 'wissen', 'wasser', 'groß', 'heiß'}

# Initialize Wordlist
wordlist_path = download_german_wordlist()
GERMAN_WORDS = load_german_wordlist(wordlist_path)

GERMAN_REPLACEMENTS = {'ue': 'ü', 'oe': 'ö', 'ae': 'ä', 'Ue': 'Ü', 'Oe': 'Ö', 'Ae': 'Ä'}

def should_replace_ss(word: str) -> bool:
    word_lower = word.lower()
    if word_lower in GERMAN_WORDS: return False
    return word_lower.replace('ss', 'ß') in GERMAN_WORDS

def smart_german_normalize(word: str) -> str:
    if not word: return word
    normalized = word
    if 'ss' in word.lower() and should_replace_ss(word):
        normalized = word.replace('SS', 'ß') if 'SS' in word else word.replace('ss', 'ß')
    for digraph, umlaut in GERMAN_REPLACEMENTS.items():
        normalized = normalized.replace(digraph, umlaut)
    return normalized

def get_language(text: str) -> str:
    """Detects language and returns ISO code (e.g., 'de', 'en', 'fr')."""
    if not text or len(text.strip()) < 3:
        return 'unknown'
    try:
        return detect(text)
    except:
        return 'unknown'

def process_german_text(text: str) -> str:
    """Performs the normalization only for German strings."""
    sentences = sent_tokenize(text)
    processed = []
    for sent in sentences:
        words = word_tokenize(sent, language='german')
        normalized = [smart_german_normalize(w) if w.isalpha() else w for w in words]
        joined = ' '.join(normalized)
        processed.append(re.sub(r'\s+([.,!?;:])', r'\1', joined))
    return ' '.join(processed)




def language_spelling_cleanup(df):

    # Ensure consistent results from language detection
    DetectorFactory.seed = 42

    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/words')
    except LookupError:
        nltk.download('punkt')
        nltk.download('punkt_tab')
        nltk.download('words')
    # 1. Detect Language (New Column)
    print("Detecting languages...")
    df['language'] = df['content'].apply(get_language)

    # 2. Clean text (Only if German)
    print("Normalizing German text...")
    df['content_cleaned'] = df.apply(
        lambda row: process_german_text(row['content']) if row['language'] == 'de' else row['content'], 
        axis=1
    )

   
    print("\n" + "="*95)
    print(f"{'LANGUAGE':<10} | {'ORIGINAL':<35} | {'CLEANED/NORMALIZED'}")
    print("-" * 95)
    for _, row in df.iterrows():
        orig = (row['content'][:32] + '..') if len(row['content']) > 32 else row['content']
        print(f"{row['language']:<10} | {orig:<35} | {row['content_cleaned']}")
    print("="*95)
    return df

