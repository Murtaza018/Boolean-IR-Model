import nltk
from nltk.stem import PorterStemmer
import string
import re

#initialize the porter stemmer
stemmer = PorterStemmer()

#returns stopwords into a list
def getStopWords():
    #open stopword file for reading
    with open("Stopword-List.txt","r") as file:
        #split the file into words
        words=file.read().split()
        #return list
        return words 
    #if error occurs in file opening    
    return -1

def preprocess_word(word):
    word = word.lower()
    word = word.translate(str.maketrans('', '', string.punctuation))
    stemmer = PorterStemmer()
    stemmed_word = stemmer.stem(word)
    return stemmed_word

def createIndex(stopWords):
    print(stopWords)
    index={}
    i=1
    while True:
        print("i:",i)
        filename=str(i)+".txt"
        try:
            with open("Abstracts/" + filename,"r") as file:
                print(filename + " Found!")
                words=file.read().split()
                for j in range(len(words)):
                    stemmed_word=preprocess_word(words[j])
                    if stemmed_word not in stopWords:
                        if stemmed_word not in index:
                            index[stemmed_word]={}
                            index[stemmed_word][i]=[j]
                        else:
                            if i not in index[stemmed_word]:
                                #index[stemmed_word]={}
                                index[stemmed_word][i]=[]
                                index[stemmed_word][i].append(j)
                            else:
                                index[stemmed_word][i].append(j)  
                                
        except FileNotFoundError:
            print(filename + " Not Found!")
            #break
        i+=1
        if(i>=3):
            break    
    return index    
def getDocumentList(index,word):
    stemmed_word=preprocess_word(word)
    if stemmed_word in index:
        return index[stemmed_word]


def validateQuery(query):
    if not query or query.strip() == "":
        return False

    tokens = query.split()
    prev_token = ""
    prev_was_operator = False
    prev_was_slash = False
    word_count = 0

    for i, token in enumerate(tokens):
        token_lower = token.lower()
        
        if token_lower in ("and", "or", "not", "/"):
            # Check operator placement
            if i == 0 or i == len(tokens) - 1:
                return False  # Operators should not be at start or end
            
            if token_lower in ("and", "or"):
                if prev_was_operator or prev_was_slash:
                    return False  # Disallow consecutive operators
            
            if token_lower == "not":
                if not (i < len(tokens) - 1 and tokens[i + 1].isalnum()):
                    return False  # NOT must be followed by a word
            
            if token == "/":
                if i < 2 or not tokens[i - 1].isdigit() or not tokens[i - 2].isalnum():
                    return False  # / must follow a word and be followed by a number
                prev_was_slash = True
            else:
                prev_was_slash = False
            
            prev_was_operator = True
        else:
            # Check for valid words
            if not token.isalnum():
                return False  # Disallow invalid characters
            
            word_count += 1
            prev_was_operator = False
            prev_was_slash = False
        
        prev_token = token
    
    return True




#store the stop word list returned from getStopWords function into stopWordList
stopWordList=getStopWords()

#check if stopWordList contains error or not
if(stopWordList==-1):
    print("Failed to retreive stopwords")
else:
    print("Stopword List initialized")  

indexing=createIndex(stopWordList)
#print("index:",indexing)

print("Search Query Constraints")
print("1-Queries can have AND,OR,NOT,/k operators")
print("  A-AND:used between 2 words if documents must include both words")
print("  B-OR:used between 2 words if documents must include either or both words")
print("  C-NOT:used before a word if documents must not include this word")
print("  D-/k:used after 2 words if documents must include both those words and at most k words can appear between them(where k>=0)")
print("2-Maximum 3 search words")
queries = [
    "word1",
    "word1 AND word2",
    "word1 OR word2",
    "word1 NOT word2",
    "word1 AND NOT word2",
    "NOT word1 AND word2",
    "word1 OR NOT word2",
    "NOT word1 OR word2",
    "word1 AND word2 AND word3",
    "word1 OR word2 OR word3",
    "word1 NOT word2 AND word3",
    "word1 word2 /3",
    "word1 word2 /1",
    "NOT word1 word2 /2",
    "",  # empty
    " ",  # whitespace only
    "AND word1",
    "word1 AND",
    "word1 AND OR word2",
    "word1 OR AND word2",
    "NOT AND word1",
    "word1 NOT AND word2",
    "word1 AND NOT /3",
    "word1 AND NOT OR word2",
    "word1 word2 /",
    "word1 word2 /word3",
    "word1 word2 / 3 word3",
    "/3 word1 word2",
    "word1 word2 /3 /2",
    "word1 /3 word2",
    "word1 word2 word3 word4",
    "word1 & word2",
    "word1 word2",
    "word1 NOT",
    "word1 NOT /3",
    "word1 NOT NOT word2"
]
for i in range(len(queries)):
    print(queries[i] + ":",validateQuery(queries[i]))
        

"""
def validateQuery(query):
    # Check for empty query or whitespace-only query
    if len(query) == 0 or query.strip() == "":
        return False

    # Split the query string into a list of words (tokens)
    words = query.split()

    # Initialize a counter for the number of index terms (words)
    i = 0

    # Iterate through each word (token) in the query
    for j in range(len(words)):

        # Check if the number of index terms exceeds 3 (maximum allowed)
        if i > 3:
            return False  # If more than 3 words, the query is invalid

        # Check if it's the first word in the query
        if j == 0:
            # The first word cannot be a boolean operator (AND, OR) or a positional operator (/)
            # unless it is NOT
            if words[j].lower() == "and" or words[j].lower() == "or" or words[j][0] == "/":
                return False  # Invalid first word

            # If the first word is not "NOT", it's considered an index term
            elif words[j].lower() != "not":
                i += 1  # Increment the index term counter

        # Check if the current word is an index term (not an operator)
        if words[j].lower() != "and" and words[j].lower() != "or" and words[j][0] != "/" and words[j].lower() != "not":
            # If it's not the first word, and the previous word was also an index term, it's invalid
            if j > 0 and (words[j - 1].lower() != "and" and words[j - 1].lower() != "or" and words[j - 1][0] != "/" and words[j - 1].lower() != "not"):
                return False  # Consecutive index terms (without operators) are invalid
            i += 1  # Increment the index term counter

        # Check if the current word is a boolean operator (AND, OR, NOT)
        if words[j].lower() == "and" or words[j].lower() == "or" or words[j].lower() == "not":
            # Check if the next word is also an operator (invalid)
            if j + 1 < len(words) and (words[j + 1].lower() == "and" or words[j + 1].lower() == "or" or words[j + 1][0] == "/"):
                return False  # Consecutive operators are invalid

            # Check if the operator is the last word in the query (invalid)
            if j + 1 >= len(words):
                return False  # Operator at the end is invalid

        # Check if the second word is a positional operator (invalid)
        if j == 1 and words[j][0] == "/":
            return False  # Positional operator as the second word is invalid

        # Check if the current word is a positional operator (/k) and k is missing
        if j >= 2 and words[j][0] == "/" and not len(words[j]) > 1:
            return False  # Positional operator without a number is invalid

        # Check if the positional operator (/k) is preceded by operators (invalid)
        elif j >= 2 and words[j][0] == "/" and (words[j - 1].lower() == "and" or
                                               words[j - 1].lower() == "or" or words[j - 1][0] == "/" or words[j - 1].lower() == "not" or
                                               words[j - 2].lower() == "and" or words[j - 2].lower() == "or" or words[j - 2][0] == "/" or words[j - 2].lower() == "not"):
            return False  # Positional operator preceded by operators is invalid

        # Check if the positional operator (/k) is followed by a non-digit (invalid)
        elif j >= 2 and words[j][0] == "/" and not words[j][1].isdigit():
            return False  # Positional operator with non-digit distance is invalid

        # Check if there are not exactly two words before /k
        if j >= 3 and words[j][0] == "/" and (words[j - 3].lower() == "and" or words[j - 3].lower() == "or" or words[j - 3][0] == "/" or words[j - 3].lower() == "not"):
            return False #Positional operator with less than two words before is invalid.

    # If all checks pass, the query is valid
    return True"""