#-------------------------------------------------------------------------
# AUTHOR: Theoden Melgar
# FILENAME: inverted_index.py
# SPECIFICATION: 
#   This proram handles updating a term-frequency inverted index inside of 
#   MongoDB using the Python driver. The index is updated whenever
#   inserting, updating, and deleting a test document.
# FOR: CS 4250 - Assignment #3
# TIME SPENT: 2 hours
#-------------------------------------------------------------------------

# Importing Python libraries
import string
from pymongo import MongoClient

# Connecting to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Accessing the database and collections
db = client["assignment3"]
documents = db["documents"]
inverted_index = db["inverted_index"]

#-------------------------------------------------------------------------
# FUNCTION: getTermFrequencies
# SPECIFICATION: receives a text and returns the frequency of each term
#-------------------------------------------------------------------------
def getTermFrequencies(text):
    # Converting text to lowercase
    lowercase_text = text.lower()

    # Removing punctuation
    unpunctuated_text = lowercase_text.translate(str.maketrans("", "", string.punctuation))

    # Splitting the text into terms
    terms = unpunctuated_text.split()

    # Returning the term frequencies
    res = {}
    for term in terms:
        res[term] = res.get(term, 0) + 1
    return res

#-------------------------------------------------------------------------
# FUNCTION: addPosting
# SPECIFICATION: adds a posting to an existing term or creates a new term
#-------------------------------------------------------------------------
def addPosting(term, docId, tf):
    # Searching for the term in the inverted index
    term_document = inverted_index.find_one({ "term": term })

    # Creating a new term if it does not exist
    if term_document is None:
        inverted_index.insert_one({
            "term": term,
            "postings": [
                {
                    "docId": docId,
                    "tf": tf
                }
            ]
        })
    else:
        # Adding a posting if the term already exists
        inverted_index.update_one(
            { "_id": term_document["_id"] },
            { "$push": { 
                "postings": {
                    "docId": docId,
                    "tf": tf
                }
            }}
        )

#-------------------------------------------------------------------------
# FUNCTION: removePosting
# SPECIFICATION: removes a document posting from a term and deletes the
#                term if its postings list becomes empty
#-------------------------------------------------------------------------
def removePosting(term, docId):
    # Removing the posting from the term
    inverted_index.update_one(
        { "term": term },
        { "$pull": { "postings": { "docId": docId } }}
    )

    # Retrieving the term after removing the posting
    term_document = inverted_index.find_one({ "term": term })

    # Deleting the term if its postings list is empty
    if len(term_document["postings"]) == 0:
        inverted_index.delete_one({ "_id": term_document["_id"] })

#-------------------------------------------------------------------------
# FUNCTION: insertDocument
# SPECIFICATION: inserts a document and updates the inverted index
#-------------------------------------------------------------------------
def insertDocument(document):
    # Inserting the document into the documents collection
    documents.insert_one(document)
    docId = document["_id"]

    # Obtaining the term frequencies
    term_frequencies = list(getTermFrequencies(document["text"]).items())

    # Updating the inverted index
    for term_and_frequency in term_frequencies:
        term = term_and_frequency[0]
        frequency = term_and_frequency[1]
        addPosting(term, docId, frequency)

#-------------------------------------------------------------------------
# FUNCTION: updateDocument
# SPECIFICATION: updates a document and makes the corresponding changes
#                to the inverted index
#-------------------------------------------------------------------------
def updateDocument(docId, newText):
    # Retrieving the current document
    document = documents.find_one({ "_id": docId })

    # Obtaining the old and new term frequencies
    old_term_frequencies = getTermFrequencies(document["text"])
    new_term_frequencies = getTermFrequencies(newText)

    old_terms = set(old_term_frequencies.keys())
    new_terms = set(new_term_frequencies.keys())

    # Processing terms that existed in the old document
    deleted_terms = old_terms.difference(new_terms)
    for deleted_term in deleted_terms:
        removePosting(deleted_term, docId)

    existing_terms = old_terms.intersection(new_terms)
    for existing_term in existing_terms:
        new_tf = new_term_frequencies[existing_term]
        if new_tf != old_term_frequencies[existing_term]:
            inverted_index.update_one(
                { "term": existing_term, "postings.docId": docId },
                { "$set": { "postings.$.tf": new_tf }}
            )

    # Processing terms that occur only in the new document
    added_terms = new_terms.difference(old_terms)
    for added_term in added_terms:
        tf = new_term_frequencies[added_term]
        addPosting(added_term, docId, tf)

    # Updating the document text
    documents.update_one({ "_id": docId }, { "$set": { "text": newText }})

#-------------------------------------------------------------------------
# FUNCTION: deleteDocument
# SPECIFICATION: deletes a document and removes all of its postings from
#                the inverted index
#-------------------------------------------------------------------------
def deleteDocument(docId):
    # Retrieving the document before deleting it
    document = documents.find_one({ "_id": docId })

    # Obtaining the terms contained in the document
    term_frequency = getTermFrequencies(document["text"])
    terms = term_frequency.keys()

    # Removing the document from every corresponding posting list
    for term in terms:
        inverted_index.update_one(
            { "term": term }, 
            { "$pull": { "postings": { "docId": docId } } 
        })

    # Deleting the document
    documents.delete_one({ "_id": docId })

#-------------------------------------------------------------------------
# Executing the sequence of operations
#-------------------------------------------------------------------------

# Operation 1: document 1 is obtained
document1 = {
    "_id": 1,
    "text": "Summer rain is common in Florida."
}

insertDocument(document1)


# Operation 2: document 2 is obtained
document2 = {
    "_id": 2,
    "text": "Summer is hot in Arizona."
}

insertDocument(document2)


# Operation 3: document 1 is updated
updateDocument(
    1,
    "Summer rain is hot rain in Florida."
)


# Operation 4: document 3 is obtained
document3 = {
    "_id": 3,
    "text": "Hot summer rain in California."
}

insertDocument(document3)


# Operation 5: document 2 is deleted
deleteDocument(2)

# Operation 6: print the content of the documents and inverted_index collections
print("##### Documents Collection #####")
for doc in documents.find():
    print(doc)
print("##### Inverted Index Collection #####")
for index in inverted_index.find():
    print(index)