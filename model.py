import nltk
from nltk.stem import PorterStemmer
import string

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
                    stemmed_word=stemmer.stem(words[j])
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
    print ("index:",index)    
    #dict = {}
   # dict["hello"] = {} 
   # dict["hello"]["world"] = [] 
    #dict["hello"]["world"].append(102) 
    #dict["hello"]["world"].append(104)  
    #print(dict["hello"]["world"])   


#store the stop word list returned from getStopWords function into stopWordList
stopWordList=getStopWords()

#check if stopWordList contains error or not
if(stopWordList==-1):
    print("Failed to retreive stopwords")
else:
    print("Stopword List initialized")  

createIndex(stopWordList)
