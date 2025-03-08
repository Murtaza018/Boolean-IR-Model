import nltk
from nltk.stem import PorterStemmer
import string
import re
import math

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
    index={}
    i=1
    while True:
        filename=str(i)+".txt"
        try:
            with open("Abstracts/" + filename,"r") as file:

                text=file.read()
                words = []
                for word in re.split(r'[,\s/]+', text):  # Split by whitespace first
                    if '-' in word:
                        parts = word.split('-')
                        words.append(word.replace('-', ''))  # Combined word
                        words.extend(parts)  # Separate parts
                    else:
                        words.append(word)
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
            break
        i+=1
           
    return index    

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
         

        # Check if it's the first word in the query
        if j==0:
        # The first word cannot be a boolean operator (AND, OR) or a positional operator (/)
        # unless it is NOT
            if words[0].lower() == "and" or words[0].lower() == "or" or words[0][0] == "/":
                return False  # Invalid first word

        # If the first word is not "NOT", it's considered an index term
            elif words[0].lower() != "not":
                i += 1  # Increment the index term counter
                


        # Check if the current word is an index term (not an operator)
        if j>0 and words[j].lower() != "and" and words[j].lower() != "or" and words[j][0] != "/" and words[j].lower() != "not":
            if words[j - 1][0] == "/":
                return False
            # If it's not the first word, and the previous word was also an index term, it's invalid
            if (words[j - 1].lower() != "and" and words[j - 1].lower() != "or" and words[j - 1].lower() != "not"):
                if(j+1<len(words) and words[j+1][0]=="/" and len(words[j+1])>=2 and words[j+1][1].isdigit()):
                    i+=1
                    continue
                else:
                    return False  # Consecutive index terms (without operators) are invalid
            i += 1  # Increment the index term counter

        # Check if the current word is a boolean operator (AND, OR, NOT)
        if words[j].lower() == "and" or words[j].lower() == "or":
            # Check if the next word is also an operator (invalid)
            if j + 1 < len(words) and (words[j + 1].lower() == "and" or words[j + 1].lower() == "or" or words[j + 1][0] == "/"):
                return False  # Consecutive operators are invalid

            # Check if the operator is the last word in the query (invalid)
            if j + 1 >= len(words):
                return False  # Operator at the end is invalid

        if(words[j].lower()=="not"):
            if j-1>=0 and (words[j-1].lower()!="and" and words[j-1].lower()!="or"):
                return False
            if j + 1 >= len(words):
                return False
            elif words[j+1].lower()=="and" or words[j + 1].lower() == "or" or words[j + 1][0] == "/" or words[j+1].lower()=="not":
                return False    
        # Check if the second word is a positional operator (invalid)
        if j == 1 and words[j][0] == "/":
            return False  # Positional operator as the second word is invalid

        # Check if the current word is a positional operator (/k) and k is missing
        if j >= 2 and words[j][0] == "/" and not len(words[j]) > 1:
            return False  # Positional operator without a number is invalid

        # Check if the positional operator (/k) is preceded by operators (invalid)
        elif j >= 2 and words[j][0] == "/" and (words[j - 1].lower() == "and" or
                                               words[j - 1].lower() == "or" or words[j - 1][0] == "/" or words[j - 1].lower() == "not" or
                                               words[j - 2].lower() == "and" or words[j - 2].lower() == "or" or words[j - 2][0] == "/" or 
                                               words[j - 2].lower() == "not" or (j>=3 and words[j-3].lower()=="not")):
            return False  # Positional operator preceded by operators is invalid

        # Check if the positional operator (/k) is followed by a non-digit (invalid)
        elif j >= 2 and words[j][0] == "/" and not words[j][1].isdigit():
            return False  # Positional operator with non-digit distance is invalid
    
    if i > 3:
            return False

    print("i",i)
    # If all checks pass, the query is valid
    return True

def getTotalDocumentList(abc):
    doc_list = []
    for inner in abc:
        for key in inner.keys():
            if key not in doc_list:
                doc_list.append(key)
    return doc_list
def getDocumentPostings(index,stemmed_word):
    if stemmed_word in index:
        return index[stemmed_word]
    return []    
def spaceBetweenListings(list1,list2,space):
    l1=list(list1.keys())
    l2=list(list2.keys())
    
    i=0
    j=0
    skip1=math.floor(math.sqrt(len(l1)))
    skip2=math.floor(math.sqrt(len(l2)))
    doc_list=[]
    while i<len(l1) and j<len(l2):
        if(l1[i]==l2[j]):
            print("Balsmad",list1[l1[i]])
            skip3=math.floor(math.sqrt(len(list1[l1[i]])))
            skip4=math.floor(math.sqrt(len(list2[l2[j]])))
            k=0
            l=0
            while k<len(list1[i+1]) and l<len(list2[j+1]):
                
                if list2[j+1][l]>list1[i+1][k] and list2[j+1][l]-list1[i+1][k]-1<=space:
                    
                    doc_list.append(i+1)
                    i+=1
                    j+=1
                    break
                elif list2[j+1][l]<=list1[i+1][k]:
                    if l+skip4<len(list2[j+1]) and list2[j+1][l+skip4]<=list1[i+1][k]: 
                        l=l+skip4
                    else:
                        l+=1
                elif list2[j+1][l]>list1[i+1][k]:
                    if k+skip3<len(list1[i+1]) and list2[j+1][l]>list1[i+1][k+skip3]:
                        k=k+skip3
                    else:
                        k+=1
                
                    
        elif l1[i]>l2[j]:
            if j+skip2<len(l2) and l1[i]>l2[j+skip2]:
                j=j+skip2
            else:
                j+=1    
        else:
            if i+skip1<len(l1) and l1[i+skip1]<l2[j]:
                i=i+skip1
            else:    
                i+=1                  
    return doc_list


def list_intersection(list1,list2):
    if isinstance(list1, list):
        keys1=list1
    elif isinstance(list1,dict):
        keys1=list(list1.keys())
    if isinstance(list2, list):
        keys2=list2
    elif isinstance(list2,dict):
        keys2=list(list2.keys())
    set1=set(keys1)
    set2=set(keys2)
    intersect_set=set1.intersection(set2)
    return list(intersect_set)
def list_union(list1,list2):
    if isinstance(list1, list):
        keys1=list1
    elif isinstance(list1,dict):
        keys1=list(list1.keys())
    if isinstance(list2, list):
        keys2=list2
    elif isinstance(list2,dict):
        keys2=list(list2.keys())
    set1=set(keys1)
    set2=set(keys2)
    union_set=set1.union(set2)
    return list(union_set)
def getQueryDocuments(index,query):
    totalList=getTotalDocumentList(index.values())
    words=query.split()
    doc_list1=[]
    doc_list2=[]
    not_exists=False
    and_lists=False
    or_lists=False
    for i in range(len(words)):
        if words[i][0]=="/":
            space_between=words[i].rstrip()
            space_between=space_between[1:]
            space_between=int(space_between)
            print(space_between)
            doc_list1=spaceBetweenListings(doc_list1,doc_list2,space_between)
            doc_list2=[]
        elif words[i].lower()=="and":
            and_lists=True
        elif words[i].lower()=="or":
            or_lists=True
        elif words[i].lower()=="not":
            not_exists=True
        else:
            text=preprocess_word(words[i])
            if(not_exists):
                not_exists=False
                if len(doc_list1)==0:
                    if text in index:
                        doc_list1=list(set(totalList)-set(index[text].keys())) 
                    else:
                        doc_list1=totalList       
                else:
                    if text in index:
                        doc_list2=list(set(totalList)-set(index[text].keys()))
                    else:
                        doc_list2=totalList

            else:
                if len(doc_list1)==0:
                    if i+1<len(words) and (words[i+1].lower()!="and" or words[i+1].lower()!="or"):
                        doc_list1=getDocumentPostings(index,text)
                    else:
                        if text in index:
                            doc_list1=list((index[text].keys()))   

                else:
                    
                    if i+1<len(words) and words[i+1].lower()!="and" and words[i+1].lower()!="or" and words[i+1][0]!="/":
                        doc_list2=getDocumentPostings(index,text)
                        text2=preprocess_word(index,words[i+1])
                        doc_list3=getDocumentPostings(index,text2)
                        space_between=words[i+2].rstrip()
                        space_between=space_between[1:]
                        space_between=int(space_between)
                        doc_list2=spaceBetweenListings(doc_list2,doc_list3,space_between)
                    elif i+1<len(words) and words[i+1][0]=="/":
                        doc_list2=getDocumentPostings(index,text)
                    else:
                        if text in index:
                            doc_list2= list(index[text].keys())
                        elif and_lists:
                            doc_list1=[]
                        elif or_lists:
                            or_lists=False


        if len(doc_list1)>0 and len(doc_list2)>0:
            if and_lists:
                and_lists=False
                doc_list1=list_intersection(doc_list1,doc_list2)
                doc_list2=[]
            elif or_lists:
                doc_list1=list_union(doc_list1,doc_list2)
                doc_list2=[]
                or_lists=False    
   
    return doc_list1


#store the stop word list returned from getStopWords function into stopWordList
stopWordList=getStopWords()

#check if stopWordList contains error or not
if(stopWordList==-1):
    print("Failed to retreive stopwords")
else:
    print("Stopword List initialized")  

print("Creating Index...")
indexing=createIndex(stopWordList)
print("Index Created")

print("Search Query Constraints")
print("1-Queries can have AND,OR,NOT,/k operators")
print("  A-AND:used between 2 words if documents must include both words")
print("  B-OR:used between 2 words if documents must include either or both words")
print("  C-NOT:used before a word if documents must not include this word")
print("  D-/k:used after 2 words if documents must include both those words and at most k words can appear between them(where k>=0)")
print("2-Maximum 3 search words")



while(True):
    query=input("Enter Query:")
    if(validateQuery(query)):
        print("Correct Query!")
        print("Searching...")
        documents=getQueryDocuments(indexing,query)
        documents.sort()
        print("Result-Set:",documents)
        
    else:
        print("Invalid Query!")            
