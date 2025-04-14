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
#function to pre process words from the query
def preprocess_word(word):
    #lowercase all letters
    word = word.lower()
    #remove all punctuations in the word
    word = word.translate(str.maketrans('', '', string.punctuation))
    #initialize porter stemmer
    stemmer = PorterStemmer()
    #stem the word
    stemmed_word = stemmer.stem(word)
    #return stemmed word
    return stemmed_word

#function to create inverted indexings from the abstract files
def createIndex(stopWords):
    index={}
    i=1
    #loop to access file by file
    while True:
        #create filename
        filename=str(i)+".txt"
        try:
            #open file for reading
            with open("Abstracts/" + filename,"r") as file:
                #read file data into text
                text=file.read()
                #initialize words which will hold data from text after splitting into individual words
                words = []
                #Split by whitespace,comma and forward slashes
                for word in re.split(r'[,\s/]+', text): 
                    #check for hyphens in word 
                    if '-' in word:
                        #if hyphens exist store it as 1 whole word and individual words(for e.g hello-world will be stored as helloworld,hello,world 3 different indexes) 
                        parts = word.split('-')
                        #Combined word
                        words.append(word.replace('-', '')) 
                        #Separate parts 
                        words.extend(parts)  
                    else:
                        #append word directly if hyphen does not exist
                        words.append(word)
                #loop to access words 1 by 1,apply stemmer and create index for it       
                for j in range(len(words)):
                    #stem word at index j
                    stemmed_word=preprocess_word(words[j])
                    #check if word is not a stopword
                    if stemmed_word not in stopWords:
                        #check if stemmed word does not already exists in index
                        if stemmed_word not in index:
                            #create new entry for stemmed word
                            index[stemmed_word]={}
                            #store its document number and its position in the document
                            index[stemmed_word][i]=[j]
                        #if stemmed word already exists    
                        else:
                            #check if document does not already exist at stemmed word in index
                            if i not in index[stemmed_word]:
                                #create new entry for the document
                                index[stemmed_word][i]=[]
                                #append the position of the stemmed word in the index at document i
                                index[stemmed_word][i].append(j)
                            #if document already exists    
                            else:
                                #append the position of the stemmed word
                                index[stemmed_word][i].append(j)  
        #if file not found                        
        except FileNotFoundError:
            #break loop
            break
        i+=1
    #return the final index       
    return index    
#function to check if given query is valid
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
            #positional operator before an index term is false
            if words[j - 1][0] == "/":
                return False
            # If it's not the first word, and the previous word was also an index term, it's invalid
            if (words[j - 1].lower() != "and" and words[j - 1].lower() != "or" and words[j - 1].lower() != "not"):
                #unless there is a positional operator after the 2 words
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
        # check to see if word is NOT operator
        if(words[j].lower()=="not"):
            #if before NOT operator is not AND or OR operator,return False
            if j-1>=0 and (words[j-1].lower()!="and" and words[j-1].lower()!="or"):
                return False
            #if NOT operator exists as last term in the query,return false
            if j + 1 >= len(words):
                return False
            #if NOT has another operator after it,return false
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
    #if number of terms greater than 3,return false
    if i > 3:
            return False

    # If all checks pass, the query is valid
    return True

#function to get all distinct document numbers in a list(used to index term preceeded by a NOT operator)
#receives all the values from the index dictionary
def getTotalDocumentList(abc):
    doc_list = []
    #loop to traverse over every dictionary value (postings lists of a term)
    for inner in abc:
        #loop to traverse over every key in a single value item (document IDs the term exists in)
        for key in inner.keys():
            #if key does not already exists in total document list,add it
            if key not in doc_list:
                doc_list.append(key)            
    return doc_list

#function to get all postings including the postional index of a query term
def getDocumentPostings(index,stemmed_word):
    #if term exists in index,return its postings
    if stemmed_word in index:
        return index[stemmed_word]
    #if it does not exist,return empty list
    return []    

#function to get document list where 2 words are separated by a specified space in any documents (for e.g word1 word2 /5)
def spaceBetweenListings(list1,list2,space):
    #create 2 lists to store all keys from the document postings
    l1=list(list1.keys())
    l2=list(list2.keys())
    
    i=0
    j=0
    #create skip pointers for possible skips over documents
    skip1=math.floor(math.sqrt(len(l1)))
    skip2=math.floor(math.sqrt(len(l2)))
    #initialize empty document list
    doc_list=[]
    #loop to traverse both key lists until any is finished
    while i<len(l1) and j<len(l2):
        #check if both lists have a common document
        if(l1[i]==l2[j]):
            #create skips for possible skips over positional indexes
            skip3=math.floor(math.sqrt(len(list1[l1[i]])))
            skip4=math.floor(math.sqrt(len(list2[l2[j]])))
            k=0
            l=0
            #loop to traverse the postional indexes of the terms in the same document
            while k<len(list1[l1[i]]) and l<len(list2[l2[j]]):
                #check if the distance between the terms is less than or equal to the specified space
                if abs(list2[l2[j]][l]-list1[l1[i]][k])-1<=space:
                    #include the document in document list 
                    doc_list.append(l1[i])
                    break
                #check to see if document ID of list 2 is less than or equal to than document ID of list 1
                elif list2[l2[j]][l]<=list1[l1[i]][k]:
                    #check to see a skip is possible in list 2
                    if l+skip4<len(list2[l2[j]]) and list2[l2[j]][l+skip4]<=list1[l1[i]][k]:
                        
                        l=l+skip4
                    #if skip not possible increment 1    
                    else:
                        l+=1
                #check to see if document ID of list 1 is less than document ID of list 2        
                elif list2[l2[j]][l]>list1[l1[i]][k]:
                    #check to see if a skip is possible in list 1
                    if k+skip3<len(list1[l1[i]]) and list2[l2[j]][l]>list1[l1[i]][k+skip3]:
                        k=k+skip3
                    #if skip not possible increment 1    
                    else:
                        k+=1
            #inner loop ends,increment i and j to check next document in both document lists
            i+=1
            j+=1    
        #check to see if document ID of list1 is greater than document ID of list2            
        elif l1[i]>l2[j]:
            #check to see if l2 can skip over a few documents(if the skip element is less than the l1 document ID)
            if j+skip2<len(l2) and l1[i]>l2[j+skip2]:
                j=j+skip2
            #if skip not possible,increment 1
            else:
                j+=1    
        #no condition true,means l1 document ID is less than l2 document ID        
        else:
            #check to see if l1 can skip over a few documents(if the skip element is less than the l2 document ID)
            if i+skip1<len(l1) and l1[i+skip1]<l2[j]:
                i=i+skip1
            #if skip not possible,increment 1    
            else:    
                i+=1                 
                 
    return doc_list

#function to handle intersection(AND operator)
def list_intersection(list1,list2):
    #check to see if list1 is list or dict and get keys(document ID the index term appears in)
    if isinstance(list1, list):
        keys1=list1
    elif isinstance(list1,dict):
        keys1=list(list1.keys())
    #check to see if list2 is list or dict and get keys(document ID the index term appears in)  
    if isinstance(list2, list):
        keys2=list2
    elif isinstance(list2,dict):
        keys2=list(list2.keys())
    #convert both document ID lists to sets for intersection
    set1=set(keys1)
    set2=set(keys2)
    #intersect the 2 sets
    intersect_set=set1.intersection(set2)
    #convert the intersect set to a list and return
    return list(intersect_set)

#function to handle union(OR operator)
def list_union(list1,list2):
    #check to see if list1 is list or dict and get keys(document ID the index term appears in)   
    if isinstance(list1, list):
        keys1=list1
    elif isinstance(list1,dict):
        keys1=list(list1.keys())
    #check to see if list2 is list or dict and get keys(document ID the index term appears in)  
    if isinstance(list2, list):
        keys2=list2
    elif isinstance(list2,dict):
        keys2=list(list2.keys())
    #convert both document ID lists to sets for union
    set1=set(keys1)
    set2=set(keys2)
    #union the lists
    union_set=set1.union(set2)
    #convert the union set to a list and return
    return list(union_set)

#function that takes query and returns the relevant documents needed
def getQueryDocuments(index,query):
    #get all document IDs in the indexing(to solve NOT operator)
    totalList=getTotalDocumentList(index.values())
    #split the query to words
    words=query.split()
    #initialize 2 document lists for operator processing between 2 Index terms
    doc_list1=[]
    doc_list2=[]
    #initialize boolean variables to identify which operator to perform 
    not_exists=False
    and_lists=False
    or_lists=False
    #loop to traverse each query term
    for i in range(len(words)):
        #check if query term is positional operator
        #since validate query checks there are 2 terms before postional operator so this condition will not be 
        #true until 2 words are traversed and both doc list1 and doc list2 are populated
        if words[i][0]=="/":
            #get the space allowed between the 2 terms
            space_between=words[i].rstrip()
            space_between=space_between[1:]
            space_between=int(space_between)
            #call the function to find documents and store in doc_list1
            doc_list1=spaceBetweenListings(doc_list1,doc_list2,space_between)
            #empty doc list2
            doc_list2=[]
        #if query term is AND operator,make and_list bool variable true
        #will identify that 2 query terms have to be intersected(AND)     
        elif words[i].lower()=="and":
            and_lists=True
        #if query term is OR operator,make or_list bool variable true
        #will identify that 2 query terms have to be union(OR)     
        elif words[i].lower()=="or":
            or_lists=True
        #if query term is NOT operator,make not_exists bool variable true
        #will identify if a an index term in query will need NOT applied or not
        elif words[i].lower()=="not":
            not_exists=True
        #if all false,means it is an index term    
        else:
            #process the word(lowercase,remove punctuations,stemming)
            text=preprocess_word(words[i])
            #check if term has NOT before it
            if(not_exists):
                #if NOT exists,change it to false for next possible term
                not_exists=False
                #check if doc list1 is empty(this is the first term in query)
                if len(doc_list1)==0:
                    #if term exists in index
                    if text in index:
                        #set doc list1 to total document list and remove all document IDs the term is found in(NOT operator) 
                        doc_list1=list(set(totalList)-set(index[text].keys())) 
                    #term does not exist in index    
                    else:
                        #set doc list1 to total document list(NOT operator)
                        doc_list1=totalList       
                #doc list1 is not empty(this term is 2nd or later term)
                else:
                    #if term exists in index
                    if text in index:
                        #set doc list2 to total document list and remove all document IDs the term is found in(NOT operator) 
                        doc_list2=list(set(totalList)-set(index[text].keys()))
                    #term does not exist in index
                    else:
                        #set doc list1 to total document list(NOT operator)
                        doc_list2=totalList
            #NOT operator is not applied
            else:
                #check if doc list1 is empty(this is the first term in query)
                if len(doc_list1)==0:
                    #check to see if next word is another index term(possible /k query)
                    if i+1<len(words) and (words[i+1].lower()!="and" or words[i+1].lower()!="or"):
                        #set doc list1 to document postings list of the index term
                        doc_list1=getDocumentPostings(index,text)
                    #query ended or AND or OR exists
                    else:
                        #if term exists in index
                        if text in index:
                            #set doc list1 to the keys(document IDs) of the term's postings list
                            doc_list1=list((index[text].keys()))   
                #doc list1 is not empty(this term is 2nd or later term)
                else:
                    #check to see if next term is another index term(possible /k operator)
                    #example query (word1 AND word2 word3 /4,word1 AND word2 can not be solved before)
                    if i+1<len(words) and words[i+1].lower()!="and" and words[i+1].lower()!="or" and words[i+1][0]!="/":
                        #get document postings of the term
                        doc_list2=getDocumentPostings(index,text)
                        #process the next term
                        text2=preprocess_word(index,words[i+1])
                        #get document postings of the next term
                        doc_list3=getDocumentPostings(index,text2)
                        #get the allowed space
                        space_between=words[i+2].rstrip()
                        space_between=space_between[1:]
                        space_between=int(space_between)
                        #get the relevant documents 
                        doc_list2=spaceBetweenListings(doc_list2,doc_list3,space_between)
                        #increment the loop counter so this query is not accessed again
                        i+=2
                    #check to see if next operator is positional operator    
                    elif i+1<len(words) and words[i+1][0]=="/":
                        #get document postings of the term
                        doc_list2=getDocumentPostings(index,text)
                    #AND or OR operator exists
                    else:
                        #check if term exists in index
                        if text in index:
                            #get document IDs of the term
                            doc_list2= list(index[text].keys())
                        #if does not exist,check if the operator to be applied between doc list1 and doc list2 is AND or OR
                        #if operator is AND
                        elif and_lists:
                            #empty doc list1 since no common documents exist
                            doc_list1=[]
                        #if operator is OR    
                        elif or_lists:
                            #set bool to false,doc list1 remains same as before,doc list2 remains empty
                            or_lists=False

        #check if doc list1 and doc list2 are non-empty
        if len(doc_list1)>0 and len(doc_list2)>0:
            #check if operator is AND
            if and_lists:
                #false the boolean variable
                and_lists=False
                #intersect the 2 lists
                doc_list1=list_intersection(doc_list1,doc_list2)
                #empty doc list2 to hold postings of next possible term
                doc_list2=[]
            #check if operator is OR    
            elif or_lists:
                #union the 2 lists
                doc_list1=list_union(doc_list1,doc_list2)
                #empty doc list2 to hold postings of next possible term
                doc_list2=[]
                #false the boolean variable
                or_lists=False    
   #return the final document lists containing needed document IDS
    return doc_list1


#store the stop word list returned from getStopWords function into stopWordList
stopWordList=getStopWords()

#check if stopWordList contains error or not
if(stopWordList==-1):
    print("Failed to retreive stopwords")
else:
    print("Stopword List initialized")  

print("Creating Index...")
#create the indexings of all documents in Abstracts folder
indexing=createIndex(stopWordList)
print("Index Created")


print("Search Query Constraints")
print("1-Queries can have AND,OR,NOT,/k operators")
print("  A-AND:used between 2 words if documents must include both words")
print("  B-OR:used between 2 words if documents must include either or both words")
print("  C-NOT:used before a word if documents must not include this word")
print("  D-/k:used after 2 words if documents must include both those words and at most k words can appear between them(where k>=0)")
print("2-Maximum 3 search words")


#loop to keep asking for search queries
while(True):
    #input query
    query=input("Enter Query:")
    #validate the query
    if(validateQuery(query)):
        print("Correct Query!")
        print("Searching...")
        #get relevant documents
        documents=getQueryDocuments(indexing,query)
        #sort the document lists
        documents.sort()
        #print the document list
        print("Result-Set:",documents)
    #if query validation is false    
    else:
        print("Invalid Query!")            
