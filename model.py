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
    #check for empty query or whitespace
    if(len(query)==0 or query.lstrip()=="" or query.lstrip==" "):
        return False
    words=query.split()
    i=0

    for j in range(len(words)):
        #check for maximum 3 words
        if(i>3):
            print("1")
            return False
        #check for 1st word
        if(j==0):
            #1st word can not be an operator other than not
            if(words[j].lower()=="and" or words[j].lower()=="or" or words[j][0]=="/"):
                print("2")
                return False
            #if word is not 'not' it is an index term
            elif(words[j].lower()!="not"):
                i+=1
        #check to see if it is an index term
        if(words[j].lower()!="and" and words[j].lower()!="or" and words[j][0]!="/" and words[j].lower()!="not"):
            if(j>0 and (words[j].lower()!="and" and words[j].lower()!="or" and words[j][0]!="/" and words[j].lower()!="not")):
                print("9")
                return False
            i+=1
        #check to see if it is an operator other than '/k'
        if(words[j].lower()=="and" or words[j].lower()=="or" or words[j].lower()=="not"):
            #check to see if after operator another operator exists
            if(j+1<len(words) and (words[j+1].lower()=="and" or words[j+1].lower()=="or" or words[j+1][0]=="/")):
                print("3")
                return False
            if(j+1>=len(words)):
                print("6")
                return False   
        if(j==1 and words[j][0]=="/"):
            print("8")
            return False                  
        #check to see if operator is '/k' and k is a positive integer
        if(j>=2 and words[j][0]=="/" and not len(words[j])>1):
            print("4")
            return False
           
        #if it is an integer check if the 2 words before '/k' are not operators
        elif(j>=2 and words[j][0]=="/" and (words[j-1].lower()=="and" or 
        words[j-1].lower()=="or" or words[j-1][0]=="/" or words[j-1].lower()=="not" or
        words[j-2].lower()=="and" or words[j-2].lower()=="or" or words[j-2][0]=="/" or words[j-2].lower()=="not")):
            print("5")
            return False
        elif(j>=2 and words[j][0]=="/" and not words[j][1].isdigit()):
            print("7")
            return False    
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
while True:
    searchQuery=input("Your Search Query:")
    print("Query:",searchQuery)
    print(validateQuery(searchQuery))
        


