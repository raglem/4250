#-------------------------------------------------------------------------
# AUTHOR: Theoden Melgar
# FILENAME: index.py
# SPECIFICATION: A basic python program to build an inverted index from a .csv file containing "Document" and "Text", mapping terms to relevant document IDs. 
#                   The impl only handles lemmas for words in the provided collection.csv file and simple text with one sentence.
# FOR: CS 4250 - Assignment #1
# TIME SPENT: 60min - 90min
#-------------------------------------------------------------------------

# Importing Python libraries
import pandas as pd
import string

# Reading the document collection
data = pd.read_csv("collection.csv")

# Defining the dictionary used for lemmatization
# --> add your Python code here
lemmas = {
    "homes": "home",
    "increases": "increase",
    "increasing": "increase",
    "rising": "rise",
    "sales": "sale"
}

# Creating the data structure that will store the inverted index
invertedIndex = {}

# Processing each document in the collection
for i, row in data.iterrows():

    docID = row["Document"]
    text = row["Text"]

    # Applying surface-level normalization
    def normalize(text):
        lowercase = text.lower()
        normalized = lowercase.strip(string.punctuation)
        return normalized
    normalized = normalize(text)

    # Tokenizing the document
    def tokenize(text):
        tokens = text.split()
        return tokens
    tokens = tokenize(normalized)

    # Applying lemmatization
    def lemmatize(tokens):
        for i in range(len(tokens)):
            token = tokens[i]
            if token in lemmas:
                tokens[i] = lemmas[token]
        return tokens
    lemmatized_tokens = lemmatize(tokens)

    # Building the inverted index
    def build_inverted_index(tokens):
        for token in tokens:
            if token not in invertedIndex:
                invertedIndex[token] = [docID]
            else:
                invertedIndex[token].append(docID)
    build_inverted_index(lemmatized_tokens)


# Printing the inverted index with terms ordered alphabetically
# Expected format:
# term1 : ['Doc1', 'Doc2']
# term2 : ['Doc3']
for term, docIDs in invertedIndex.items():
    print(f"{term}: {docIDs}")