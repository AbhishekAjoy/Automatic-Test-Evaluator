from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob, Word, Blobber
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
""" #from dandelion import DataTXT 
#import spacy
import nltk
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob, Word, Blobber
import string
from nltk.corpus import wordnet as wn
from nltk import word_tokenize, pos_tag

def remove_punctuation(text):
    text = "".join([c for c in text if c not in string.punctuation])
    return text

#convert sentence into list of words
def tokenize(text):
    text = word_tokenize(text)
    return text

#remove irrelevant words like is, the, etc
def remove_stopwords(text):
    sw = stopwords.words('english')
    words = [w for w in text if w not in sw]
    return words

#Converts words to its root or base form meaningfully, eg: running to run
def word_lemmatizer(text):
    lemmatizer = WordNetLemmatizer()
    t = [lemmatizer.lemmatize(i) for i in text]
    return t
#Cuts of prefixes and suffixes to reach the root word
def word_stemmer(text):
    stemmer = PorterStemmer()
    t = [stemmer.stem(i) for i in text]
    return t

#Used to detect the sentiment of two texts and compare them to detect contradictions
def sentence_polarity(text1, text2):
    t1 = TextBlob(text1)
    t2 = TextBlob(text2)
    polarity = abs(t1.sentiment.polarity - t2.sentiment.polarity)
    return polarity
#Preprocessing text by applying above functions
def preprocess(text):
    text = TextBlob(text).correct()#Correcting spelling errors
    text = remove_punctuation(text)
    text = tokenize(text)
    text = remove_stopwords(text)
    text = word_lemmatizer(text)
    text = word_stemmer(text)
    return text

#divides the number of matching keywords in student answer and reference answer divided
#by the no of keywords in the reference

def penn_to_wn(tag):
    Convert between a Penn Treebank tag to a simplified Wordnet tag
    if tag.startswith('N'):
        return 'n'
 
    if tag.startswith('V'):
        return 'v'
 
    if tag.startswith('J'):
        return 'a'
 
    if tag.startswith('R'):
        return 'r'
 
    return None
 
def tagged_to_synset(word, tag):
    wn_tag = penn_to_wn(tag)
    if wn_tag is None:
        return None
 
    try:
        return wn.synsets(word, wn_tag)[0]
    except:
        return None
 
def sentence_similarity(sentence1, sentence2):
   
    sentence1 = word_tokenize(sentence1)
    sentence2 = word_tokenize(sentence2)
    sentence1 = remove_punctuation(sentence1)
    sentence2 = remove_punctuation(sentence2)
    sentence1 = remove_stopwords(sentence1)
    sentence2 = remove_stopwords(sentence2)
    sentence1 = pos_tag(sentence1)
    sentence2 = pos_tag(sentence2)
    # Get the synsets for the tagged words
    synsets1 = [tagged_to_synset(*tagged_word) for tagged_word in sentence1]
    synsets2 = [tagged_to_synset(*tagged_word) for tagged_word in sentence2]
 
    # Filter out the Nones
    synsets1 = [ss for ss in synsets1 if ss is not None]
    synsets2 = [ss for ss in synsets2 if ss is not None]

    score, count = 0.0, 0
 
    # For each word in the first sentence
    for synset in synsets1:
        # Get the similarity value of the most similar word in the other sentence
        score_set = [synset.path_similarity(ss) for ss in synsets2]
        best_score = 0
        for i in score_set:
            if i != None and i > best_score:
                best_score = i
        # Check that the similarity could have been computed
        if best_score is not None:
            score += best_score
            count += 1
 
    # Average the values
    score /= count
    return score

def symmetric_sentence_similarity(sentence1, sentence2):
    #averaging normal and reverse similarity
    return (sentence_similarity(sentence1, sentence2) + sentence_similarity(sentence2, sentence1)) / 2 

#Converts list of words in text to vectors and calculates cosine between vectors
def cosine_sim(X,Y): 
    X_set = {w for w in X}
    Y_set = {w for w in Y}
    l1 = []
    l2 = []
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
    return(cosine)  """

#remove irrelevant words like is, the, etc
def remove_stopwords(text):
    sw = stopwords.words('english')
    words = [w for w in text if w not in sw]
    return words

def tokenize(text):
    text = word_tokenize(text)
    return text


def sentence_polarity(text1, text2):
    t1 = TextBlob(text1)
    t2 = TextBlob(text2)
    if t1.sentiment.polarity > 0 and t2.sentiment.polarity < 0:
        polarity = abs(t1.sentiment.polarity - t2.sentiment.polarity)
    elif t1.sentiment.polarity < 0 and t2.sentiment.polarity > 0:
        polarity = abs(t1.sentiment.polarity - t2.sentiment.polarity)
    else:
        polarity = 0
    polarity = polarity/2
    if polarity >= 0.5:
        polarity = 1
    return polarity

def evaluate(qapair):

    studentAnswer = qapair[0]
    question = qapair[1]
    question = tokenize(question)
    question = remove_stopwords(question)
    referenceAnswer = qapair[2]
    polarity = sentence_polarity(referenceAnswer,studentAnswer)
    #Replacing words from question from the answer
    for i in question:
        studentAnswer = studentAnswer.replace(i,"")
        referenceAnswer = referenceAnswer.replace(i,"")
    sentences = []
    sentences.append(studentAnswer)
    sentences.append(referenceAnswer)

    model_name = "paraphrase-albert-small-v2"
    model  = SentenceTransformer(model_name)

    sentence_vecs = model.encode(sentences)
    cosine =cosine_similarity(
    [sentence_vecs[0]],
    [sentence_vecs[1]]
    )

    #Evaluating sentence polarities
    """ polarity = sentence_polarity(referenceAnswer,studentAnswer)
    #Removing words from answer that are in question
    qwlist = list(question.split(" "))
    for w in qwlist:
        referenceAnswer = referenceAnswer.replace(w,'')
        studentAnswer = studentAnswer.replace(w,'')

    X = preprocess(referenceAnswer)  
    Y = preprocess(studentAnswer)
    if len(Y) == 0:
        Y = ['']
   
    cosine = cosine_sim(X,Y)
    pos_sim = symmetric_sentence_similarity(referenceAnswer, studentAnswer)
    score = pos_sim

    #if answer is correct check if the answer is a contradiction
    
    
   
    if cosine > 0.5:
        score = pos_sim

    if score > 0.5:
        score = score - score*polarity
    score = cosine """
    score = cosine[0][0]
    if score > 0.5:
        score = score - score*polarity
    if score < 0:
        score = 0
    return(score)


