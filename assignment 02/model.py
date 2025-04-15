import nltk
from nltk.stem import WordNetLemmatizer
import string
import re
import math
import os
from collections import defaultdict
import numpy as np

#constant values
ABSTRACTS_DIR = "Abstracts"
STOPWORDS_FILE = "Stopword-List.txt"
SIMILARITY_THRESHOLD = 0.05

#initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

#returns stopword set from file
def get_stop_words(filepath=STOPWORDS_FILE):
    try:
        #open file in read mode
        with open(filepath, "r") as file:
            #split the words
            words = file.read().split()
            return set(words)
    except FileNotFoundError:
        #if file not found,return null
        print(f"Error: Stopwords file not found at {filepath}")
        return set()
#process words read in documents
def preprocess_word(word):
    #return none if word is empty
    if not word:
        return None
    #lowercase the word
    word = word.lower()
    #remove all punctuations
    word = word.translate(str.maketrans('', '', string.punctuation))
    if word:
        #leematize the word according to correct vocabulary
        lemmatized_word = lemmatizer.lemmatize(word)
        return lemmatized_word
    return None

#text from a file is used in this function to create tokens
def tokenize_and_preprocess(text, stop_words):
    processed_tokens = []
    #split words based on comma,space or forward slash
    temp_words = re.split(r'[,\s/]+', text)
    words = []
    #access the words 1 by 1
    for word in temp_words:
        #check if word has hyphen
        if '-' in word and len(word) > 1:
             #if hyphen found,break the word further
             parts = word.split('-')
             #add the combined word in the temporary index after processing the word
             combined_no_hyphen = preprocess_word(word.replace('-', ''))
             if combined_no_hyphen: words.append(combined_no_hyphen)
             for part in parts:
                 #add parts of the word in the temporary index as well after processing the word and breaking the word based on hyphen
                 processed_part = preprocess_word(part)
                 if processed_part: words.append(processed_part)
        #if no hyphen,add the word in the index after processing it         
        else:
            processed = preprocess_word(word)
            if processed: words.append(processed)
    #check if the words are stopwords
    for token in words:
        if token and token not in stop_words:
             #only append those tokens in the index which are not stopwords
             processed_tokens.append(token)
    #return the final indexing of a file
    return processed_tokens


#function to build tf-idf inverted index
def build_inverted_index_and_tf_df(docs_path, stop_words):
    term_doc_freq = defaultdict(lambda: defaultdict(int))
    doc_freq = defaultdict(int)
    doc_tokens_map = {}
    doc_id_map = {}
    doc_count = 0

    try:
        #create a list of all the available files
        filenames = sorted([f for f in os.listdir(docs_path) if f.endswith(".txt")],
                           key=lambda x: int(os.path.splitext(x)[0]))
    #if fliepath is worng
    except FileNotFoundError:
        print(f"Error: Directory not found at {docs_path}")
        return {}, {}, {}, 0
    #if filenames are not numeric
    except ValueError:
        print(f"Error: Ensure filenames in {docs_path} are numeric (e.g., 1.txt, 2.txt).")
        return {}, {}, {}, 0
    #loop to token and process every file
    for filename in filenames:
        #check is file(document) is numeric or not,skip non-numeric ones
        try:
            doc_id = int(os.path.splitext(filename)[0])
        except ValueError:
            print(f"Skipping file with non-numeric name: {filename}")
            continue
        #keep document counts
        doc_count += 1
        doc_id_map[filename] = doc_id
        filepath = os.path.join(docs_path, filename)

        try:
            #open file,read file and tokenize the text
            with open(filepath, "r", encoding='utf-8', errors='ignore') as file:
                text = file.read()
                tokens = tokenize_and_preprocess(text, stop_words)
                doc_tokens_map[doc_id] = tokens
                #countr term frequency for every term
                term_counts_in_doc = defaultdict(int)
                processed_terms_in_doc = set()
                #loop to create term frequencies for every token in the file(document) index
                for token in tokens:
                    term_counts_in_doc[token] += 1
                    if token not in processed_terms_in_doc:
                        doc_freq[token] += 1
                        processed_terms_in_doc.add(token)
                #loop to create index count for every term in every document
                for term, count in term_counts_in_doc.items():
                    term_doc_freq[term][doc_id] = count

        except Exception as e:
            print(f"Error processing file {filename}: {e}")
    #no document was processed
    if doc_count == 0:
         print(f"Warning: No valid '.txt' files found or processed in '{docs_path}'.")

    print(f"Processed {doc_count} documents.")
    #return tf-idf,tf,how many tokens a document has and total number of documents
    return dict(term_doc_freq), dict(doc_freq), dict(doc_tokens_map), doc_count

#calculate term frequency
def calculate_tf(term, doc_id, term_doc_freq, doc_tokens_map):
    return term_doc_freq.get(term, {}).get(doc_id, 0)
#calculate inverse document frequency
def calculate_idf(term, doc_freq, num_docs):
    df = doc_freq.get(term, 0)
    if df == 0 or num_docs == 0:
        return 0
    return math.log(num_docs / (df + 1)) + 1
#calculate tf-idf
def calculate_tfidf(tf, idf):
    return tf * idf
#build document vectors
def build_document_vectors(term_doc_freq, doc_freq, doc_tokens_map, num_docs):
    doc_vectors = defaultdict(dict)
    # Create a set of all unique terms encountered in the corpus (the vocabulary)
    vocabulary = set(term_doc_freq.keys())

    print("Building document vectors...")
    doc_ids = list(doc_tokens_map.keys())

    # Pre-calculate IDF values for all terms in the vocabulary for efficiency
    idf_map = {term: calculate_idf(term, doc_freq, num_docs) for term in vocabulary}

    # Iterate through each document ID to build its vector
    for doc_id in doc_ids:
        # Get raw term frequencies for terms present only in the current document
        doc_tf_map = {term: term_doc_freq.get(term,{}).get(doc_id, 0)
                          for term in doc_tokens_map[doc_id] if term in vocabulary}

        vector_length_sq = 0.0 # Initialize for calculating vector magnitude

        # Calculate TF-IDF for each term in the current document
        for term, tf_raw in doc_tf_map.items():
            tf = tf_raw # Using raw term frequency
            # Retrieve the pre-calculated IDF for the term
            idf = idf_map.get(term, 0)
            # Calculate the TF-IDF score for this term in this document
            tfidf = calculate_tfidf(tf, idf)

            if tfidf > 0:
                # Store the non-zero TF-IDF weight in the document's vector 
                doc_vectors[doc_id][term] = tfidf
                # Accumulate the square of the weight for vector length calculation
                vector_length_sq += tfidf ** 2

        # Calculate the magnitude (Euclidean length) of the document vector
        magnitude = math.sqrt(vector_length_sq)
        # Normalize the document vector if its magnitude is greater than zero
        if magnitude > 0:
            # Divide each TF-IDF weight by the vector magnitude
            for term in doc_vectors[doc_id]:
                doc_vectors[doc_id][term] /= magnitude

    print("Document vectors built.")
    # Return the dictionary of normalized document vectors, the vocabulary, and the IDF map
    return dict(doc_vectors), vocabulary, idf_map

#check vector similarity
def build_query_vector(query_tokens, vocabulary, idf_map, num_docs):
    query_vector = defaultdict(float)
    term_counts_in_query = defaultdict(int)
    query_token_count = len(query_tokens)

    if query_token_count == 0:
        return {}

    # Calculate raw term frequencies for each term within the query itself
    for token in query_tokens:
        term_counts_in_query[token] += 1

    vector_length_sq = 0.0 # Initialize for calculating query vector magnitude
    # Calculate TF-IDF for each term in the query
    for term, count in term_counts_in_query.items():
        # Only consider terms that are part of the corpus vocabulary
        if term in vocabulary:
            # Use raw frequency count as TF for the query term
            query_tf = count
            # Get the pre-calculated IDF value 
            idf = idf_map.get(term, 0)
            # Calculate the TF-IDF weight for the query term
            tfidf = calculate_tfidf(query_tf, idf)

            if tfidf > 0:
                # Store the non-zero weight in the query vector 
                query_vector[term] = tfidf
                # Accumulate the square of the weight for vector length calculation
                vector_length_sq += tfidf ** 2

    # Calculate the magnitude of the query vector
    magnitude = math.sqrt(vector_length_sq)
    # Normalize the query vector if its magnitude is greater than zero
    if magnitude > 0:
        # Divide each TF-IDF weight by the vector magnitude
        for term in query_vector:
            query_vector[term] /= magnitude

    # Return the normalized query vector as a standard dictionary
    return dict(query_vector)


def cosine_similarity(vec1, vec2):
    # ensure vec1 is the shorter vector for faster intersection
    if len(vec1) > len(vec2):
        vec1, vec2 = vec2, vec1

    # Find the set of terms that are common to both vectors
    common_terms = set(vec1.keys()) & set(vec2.keys())
    # Calculate the dot product by summing the product of weights for common terms
   
    dot_product = sum(vec1[term] * vec2[term] for term in common_terms)
    # Clamp the result between -1.0 and 1.0 to handle potential floating point inaccuracies
    return max(-1.0, min(1.0, dot_product))


#process user query
def process_vsm_query(query, doc_vectors, vocabulary, idf_map, num_docs, stop_words, threshold):
    # Preprocess the raw query string into a list of relevant tokens (lemmas)
    query_tokens = tokenize_and_preprocess(query, stop_words)
    if not query_tokens:
        print("Query contains only stopwords or is empty after preprocessing.")
        return []

    # Build the normalized TF-IDF vector representation for the processed query
    query_vector = build_query_vector(query_tokens, vocabulary, idf_map, num_docs)
    if not query_vector:
         print("Query vector could not be built (e.g., all query terms are out of vocabulary).")
         return []

    results = []
    # Iterate through all pre-calculated document vectors
    for doc_id, doc_vec in doc_vectors.items():
        # Ensure the document vector is not empty
        if doc_vec:
            # Calculate the cosine similarity between the query vector and the current document vector
            similarity = cosine_similarity(query_vector, doc_vec)
            # Keep the result only if the similarity meets or exceeds the threshold
            if similarity >= threshold:
                # Store the document ID and its similarity score
                results.append((doc_id, similarity))

    # Sort the results list based on document ID in ascending order
    results.sort(key=lambda x: x[0], reverse=False)
    # Return the filtered and sorted list of (doc_id, score) tuples
    return results

#main function
if __name__ == "__main__":
    # Load the set of stopwords from the specified file
    stop_word_set = get_stop_words(STOPWORDS_FILE)
    if not stop_word_set:
        print("Proceeding without stopwords.")

    print("Initializing VSM with Lemmatization...")
    # Build the core data structures: TF per doc, DF per term, and tokens per doc
    term_doc_freq, doc_freq, doc_tokens_map, num_docs = build_inverted_index_and_tf_df(ABSTRACTS_DIR, stop_word_set)

    # Exit if no documents were successfully processed
    if num_docs == 0:
        print("No documents found. Exiting.")
    else:
        # Pre-calculate the normalized TF-IDF vectors for all documents in the corpus
        doc_vectors, vocabulary, idf_map = build_document_vectors(term_doc_freq, doc_freq, doc_tokens_map, num_docs)
        print(f"VSM Initialized. Vocabulary size: {len(vocabulary)}, Documents: {num_docs}")
        print("\nEnter your search query (e.g., 'information retrieval'). Type 'exit' to quit.")

        # Start the interactive loop to accept user queries
        while True:
            # Prompt the user for a query and remove leading/trailing whitespace
            query = input("Enter Query: ").strip()
            # Check if the user wants to exit the loop
            if query.lower() == 'exit':
                break
            # Skip if the user just pressed Enter without typing anything
            if not query:
                continue

            print("Searching...")
            # Process the query using the VSM: calculate query vector, compute similarities, filter, and sort
            ranked_docs = process_vsm_query(query, doc_vectors, vocabulary, idf_map, num_docs, stop_word_set, SIMILARITY_THRESHOLD)

            # Check if the search returned any relevant documents above the threshold
            if ranked_docs:
                print(f"\nFound {len(ranked_docs)} relevant documents (score >= {SIMILARITY_THRESHOLD}):")
                # Iterate through the sorted list of (doc_id, score) tuples
                for doc_id, score in ranked_docs:
                    # Print each relevant document ID and its calculated similarity score
                    print(f"  Document ID: {doc_id}, Score: {score:.4f}")
            else:
                # Inform the user if no documents met the similarity criteria
                print("No relevant documents found matching the criteria.")
            print("-" * 20) # Print a separator for readability