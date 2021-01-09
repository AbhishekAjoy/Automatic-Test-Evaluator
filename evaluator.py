#from dandelion import DataTXT 
import spacy
import nltk
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 

def cosine_sim(X,Y):
    # tokenization 
    X_list = word_tokenize(X)  
    Y_list = word_tokenize(Y) 
    
    # sw contains the list of stopwords 
    sw = stopwords.words('english')  
    l1 =[];l2 =[] 
    
    # remove stop words from the string 
    X_set = {w for w in X_list if not w in sw}  
    Y_set = {w for w in Y_list if not w in sw} 
    
    # form a set containing keywords of both strings  
    rvector = X_set.union(Y_set)  
    for w in rvector: 
        if w in X_set: l1.append(1) # create a vector 
        else: l1.append(0) 
        if w in Y_set: l2.append(1) 
        else: l2.append(0) 
    c = 0
    
    # cosine formula  
    for i in range(len(rvector)): 
            c+= l1[i]*l2[i] 
    cosine = c / float((sum(l1)*sum(l2))**0.5)
    return(cosine) 

def evaluate(qapair):
    try:
       nlp = spacy.load('en_core_web_md')
    except:
        return('Unable to load nlp')
    question = qapair[1]
    studentAnswer = qapair[0]
    referenceAnswer = qapair[2]
    
    #Dandelion API has limits to the number comparisons per day(approx. 333) not scalable
    #Token value changes every day
    '''
    dandelionToken = '0021d5ca5f7948fbb22a2ce2f03a4c7a'
    datatxt = DataTXT(token=dandelionToken)
    response = datatxt.sim(studentAnswer,referenceAnswer)
    return(response)
    '''
    cosine = cosine_sim(referenceAnswer,studentAnswer)
    s1 = nlp(referenceAnswer)
    s2 = nlp(studentAnswer)
    #print(s1.similarity(s2))
    return(cosine)


