import re
import unicodedata
import pandas as pd
from pyvi import ViTokenizer
# Load stopwords from text file
stop_words = pd.read_csv('../../data/vietnamese-stopwords-dash.txt', header=None)

# Text cleaning function
def clean_text(text):
    # Convert to lowercase
    text = text.lower() 
    
    # Normalize Unicode characters
    text = unicodedata.normalize('NFKC', text)
    
    # Remove characters and numbers
    text = re.sub(r'[^a-zA-ZÀ-ỹ ]+', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # tokenized_sentence = word_tokenize(text, format='text').split()  # List of words
    tokenized_sentence = ViTokenizer.tokenize(text)
   
    cleaned_sentence = ' '.join(word for word in tokenized_sentence.split() if word not in stop_words[0].tolist())
    text = ' '.join(word for word in text.split() if word not in stop_words)  # Remove stopwords
    return cleaned_sentence 