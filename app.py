import pandas as pd
import numpy as np
import os
import csv
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import syllables
import spacy
from textstat.textstat import textstatistics,legacy_round
import string
import re
import tqdm

nltk.download('punkt')
df=pd.read_excel("Input.xlsx")

def clean_text(text, stop_words):
    words = word_tokenize(text)
    cleaned_words = [word.lower() for word in words if word.isalpha() and word.lower() not in stop_words]
    return cleaned_words

# Function to create positive and negative dictionaries
def create_dictionary(file_path, stop_words):
    with open(file_path, 'r', encoding='ISO-8859-1') as file:
        words = [word.strip().lower() for word in file.readlines() if word.strip().lower() not in stop_words]
    return words

# Function to calculate sentiment scores
def calculate_scores(tokens, positive_dict, negative_dict):
    positive_score = sum(1 for word in tokens if word in positive_dict)
    negative_score = sum(1 for word in tokens if word in negative_dict)
    
    polarity_score = (positive_score - negative_score) / (positive_score + negative_score + 0.000001)
    subjectivity_score = (positive_score + negative_score) / (len(tokens) + 0.000001)
    
    return positive_score, negative_score, polarity_score, subjectivity_score

def break_sentences(text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    return list(doc.sents)
 
# Returns Number of Words in the text
def word_count(text):
    sentences = break_sentences(text)
    words = 0
    for sentence in sentences:
        words += len([token for token in sentence])
    return words
 
# Returns the number of sentences in the text
def sentence_count(text):
    sentences = break_sentences(text)
    return len(sentences)
 
# Returns average sentence length
def avg_sentence_length(text):
    words = word_count(text)
    sentences = sentence_count(text)
    average_sentence_length = float(words / sentences)
    return average_sentence_length
def syllables_count(word):
    return textstatistics().syllable_count(word)
def percentage_complex_word(text):
    return difficult_words(text)/word_count(text)
def fogindex(text):
    # Fog Index = 0.4 * (Average Sentence Length + Percentage of Complex words)
    return 0.4 * (avg_sentence_length(text) + percentage_complex_word(text))
def avg_syllables_per_word(text):
    syllable = syllables_count(text)
    words = word_count(text)
    ASPW = float(syllable) / float(words)
    return legacy_round(ASPW, 1)
def cleaned_word_count(text):
    translator = str.maketrans('', '', string.punctuation)
    no_punctuations = text.translate(translator)
    # Tokenize into words
    words = no_punctuations.split()
    # Remove stop words
    filtered_words = [word.lower() for word in words if word.lower() not in stop_words]
    # Count the remaining words
    word_count = len(filtered_words)
    return word_count
# Return total Difficult Words in a text
def difficult_words(text):
     
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    # Find all words in the text
    words = []
    sentences = break_sentences(text)
    for sentence in sentences:
        words += [str(token) for token in sentence]
    diff_words_set = set()
     
    for word in words:
        syllable_count = syllables_count(word)
        if word not in nlp.Defaults.stop_words and syllable_count >= 2:
            diff_words_set.add(word)
 
    return len(diff_words_set)


def count_personal_pronouns(input_string):
    # Define personal pronouns
    personal_pronouns = {"i", "we", "my", "ours", "us"}

    # Remove punctuations
    translator = str.maketrans('', '', string.punctuation)
    no_punctuations = input_string.translate(translator)

    # Tokenize into words
    words = no_punctuations.split()

    # Count occurrences of personal pronouns
    pronoun_count = sum(1 for word in words if word.lower() in personal_pronouns)

    return pronoun_count
def calculate_average_word_length(input_string):
    # Remove punctuations
    translator = str.maketrans('', '', string.punctuation)
    no_punctuations = input_string.translate(translator)

    # Tokenize into words
    words = no_punctuations.split()

    # Calculate total number of characters in all words
    total_characters = sum(len(word) for word in words)

    # Calculate total number of words
    total_words = len(words)

    # Calculate average word length
    if total_words > 0:
        average_word_length = total_characters / total_words
    else:
        average_word_length = 0

    return average_word_length






# Load stop words from multiple files
stop_words_folder = 'stopwords'
stop_words = set()
text_files_folder="output"
for filename in os.listdir(stop_words_folder):
    with open(os.path.join(stop_words_folder, filename), 'r', encoding='ISO-8859-1') as file:
        stop_words.update([word.strip().lower() for word in file.readlines()])

# Load positive and negative dictionaries
positive_file_path = 'positive-words.txt'
negative_file_path = 'negative-words.txt'

positive_dict = create_dictionary(positive_file_path, stop_words)
negative_dict = create_dictionary(negative_file_path, stop_words)

# Open the new CSV file for writing the updated data
with open("Output Data Structure.csv", 'w', newline='', encoding='ISO-8859-1') as csvfile:
    # Create a CSV writer object
    csv_writer = csv.writer(csvfile)

    # Write the header row for the new CSV file
    csv_writer.writerow(['URL_ID','URL','POSITIVE SCORE', 'NEGATIVE SCORE', 'POLARITY SCORE', 'SUBJECTIVITY SCORE',
                         'AVG SENTENCE LENGTH', 'PERCENTAGE OF COMPLEX WORDS', 'FOG INDEX',
                         'AVG NUMBER OF WORDS PER SENTENCE', 'COMPLEX WORD COUNT', 'WORD COUNT',
                         'SYLLABLE PER WORD', 'PERSONAL PRONOUNS', 'AVG WORD LENGTH'])

    # Process each text file in the folder
    
    for filename in tqdm.tqdm(os.listdir(text_files_folder)):
        if filename.endswith(".txt"):
            file_path = os.path.join(text_files_folder, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
            except UnicodeDecodeError:
                # Try a different encoding
                with open(file_path, 'r', encoding='ISO-8859-1') as file:
                    text = file.read()

            # Continue with the rest of your processing...
            cleaned_tokens = clean_text(text, stop_words)

            # Sentiment Analysis
            pos_score, neg_score, polarity_score, subjectivity_score = calculate_scores(cleaned_tokens, positive_dict, negative_dict)

            asl= avg_sentence_length(text)
            complex_words_percentage=percentage_complex_word(text)
            fog_index=fogindex(text)
            avg_words_per_sentence = word_count(text)/ sentence_count(text)
            complex_word_count = difficult_words(text)
            syllables_per_word = avg_syllables_per_word(text)
            avg_word_length = calculate_average_word_length(text)

            # Write the row to the new CSV file
            csv_writer.writerow([filename[:-4],df[df.URL_ID==filename[:-4]].iloc[0,1], pos_score, neg_score, polarity_score, subjectivity_score,
                                 asl, complex_words_percentage, fog_index,
                                 avg_words_per_sentence, complex_word_count, cleaned_word_count(text),
                                 syllables_per_word, count_personal_pronouns(text), avg_word_length])
