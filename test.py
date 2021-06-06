
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
def remove_stopwords(text):
    sw = stopwords.words('english')
    words = [w for w in text if w not in sw]
    return words
def tokenize(text):
    text = word_tokenize(text)
    return text
x = "Baeyer's reagent is a solution of Potassium Permanganate."
y = "What is Baeyer's reagent"
y = tokenize(y)
y = remove_stopwords(y)
print(y)
for i in y:
    print(i)
    x = x.replace(i,"")
print(x)
""" import string
import nltk
import random
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer 
from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords
from textblob import TextBlob, Word, Blobber
from nltk.corpus import wordnet as wn
from nltk import word_tokenize, pos_tag
from nltk.util import ngrams
import re
from collections import Counter
import math """

""" NGRAM = 3
re_stripper_alpha = re.compile('[^a-zA-Z]+')
def remove_punctuation(text):
    text = "".join([c for c in text if c not in string.punctuation])
    return text

def tokenize(text):
    text = word_tokenize(text)
    return text

def remove_stopwords(text):
    sw = stopwords.words('english')
    words = [w for w in text if w not in sw]
    return words
def word_lemmatizer(text):
    lemmatizer = WordNetLemmatizer()
    t = [lemmatizer.lemmatize(i) for i in text]
    return t
def word_stemmer(text):
    stemmer = PorterStemmer()
    t = [stemmer.stem(i) for i in text]
    return t
 """
""" def sentence_polarity(text1, text2):
    text1 = TextBlob(text1)
    text2 = TextBlob(text2)
    print(text1.sentiment)
    print(text2.sentiment)
    polarity = abs(text1.sentiment.polarity - text2.sentiment.polarity)
    return polarity
 """
""" def matched_keywords(text1,text2):
    n = 0
    for w1 in text1:
        for w2 in text2:
            if w1 == w2:
                n = n + 1
    match = n/len(text1) #assume text1 is reference answer
    return match
 """
""" def preprocess(text):
    text = remove_punctuation(text)
    text = tokenize(text)
    text = remove_stopwords(text)
    text = word_lemmatizer(text)
    text = word_stemmer(text)
    return text """

#print(preprocess("He was studying for the exam very rigourously, but he still couldn't pass the exam"))
""" referenceAnswer = "Smog is a mixture of smoke and fog"
qwlist = ['Smog','eggs']
for w in qwlist:
    referenceAnswer = referenceAnswer.replace(w,'')
print(referenceAnswer) """
""" X = preprocess("Biological Oxygen Demand (BOD) is the amount of oxygen present in water for sustaining life under water.")
Y = preprocess("BOD of a sample of water is defined as the amount of dissolved oxygen required for the oxidation of organic matter by aquatic micro-organisms under aerobic conditions at 241C for a period of 5 days.")
print(X)
print(Y)
match = matched_keywords(Y,X)
print(match) """
""" randomlist = []
no_of_questions = 5
for i in range(0,no_of_questions):
    n = random.randint(1001,1001+35)
    if n in randomlist:
        continue
    else:
        randomlist.append(n) """
""" X = preprocess("Biological Oxygen Demand (BOD) is the amount of oxygen present in water for sustaining life under water.")
Y = preprocess("a c ll b c l")
print(X)
print(Y) """
""" print (wn.synsets('cat', 'n'))
# [Synset('cat.n.01'), Synset('guy.n.01'), Synset('cat.n.03'), Synset('kat.n.01'), Synset('cat-o'-nine-tails.n.01'), Synset('caterpillar.n.02'), Synset('big_cat.n.01'), Synset('computerized_tomography.n.01')]
 
print (wn.synsets('dog', 'n'))
# [Synset('dog.n.01'), Synset('frump.n.01'), Synset('dog.n.03'), Synset('cad.n.01'), Synset('frank.n.02'), Synset('pawl.n.01'), Synset('andiron.n.01')]
 
print (wn.synsets('feline', 'n'))
# [Synset('feline.n.01')]
 
print (wn.synsets('mammal', 'n'))
# [Synset('mammal.n.01')]
 
 
 
# It's important to note that the `Synsets` from such a query are ordered by how frequent that sense appears in the corpus
 
# You can check out how frequent a lemma is by doing:
cat = wn.synsets('cat', 'n')[0]     # Get the most common synset
print (cat.lemmas()[0].count())       # Get the first lemma => 18
 
 
 
dog = wn.synsets('dog', 'n')[0]           # Get the most common synset
feline = wn.synsets('feline', 'n')[0]     # Get the most common synset
mammal = wn.synsets('mammal', 'n')[0]     # Get the most common synset
 
 
 
# You can read more about the different types of wordnet similarity measures here: http://www.nltk.org/howto/wordnet.html
for synset in [dog, feline, mammal]:
    print ("Similarity(%s, %s) = %s" % (cat, synset, cat.wup_similarity(synset)))

print(cat.wup_similarity(cat)) """
""" def penn_to_wn(tag):
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
    compute the sentence similarity using Wordnet
    # Tokenize and tag
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
    compute the symmetric sentence similarity using Wordnet
    return (sentence_similarity(sentence1, sentence2) + sentence_similarity(sentence2, sentence1)) / 2 
 
def get_tuples_textblob_sentences(txt):
    New get_tuples that does use textblob.
    if not txt: return None
    tb = TextBlob(txt)
    ng = (ngrams(x.words, NGRAM) for x in tb.sentences if len(x.words) > NGRAM)
    return [item for sublist in ng for item in sublist]

def jaccard_distance(a, b):
    Calculate the jaccard distance between sets A and B
    a = set(a)
    b = set(b)
    return 1.0 * len(a&b)/len(a|b)

def cosine_similarity_ngrams(a, b):
    vec1 = Counter(a)
    vec2 = Counter(b)
    
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    return float(numerator) / denominator

sentences = [
    
    "The mixture of smoke and fog is called smog",
    "Smog is smoke and fog"
]
sentence1 = "smoke together with fog is smog"
focus_sentence = "smog and smoke is smog"


print ("SymmetricSimilarity(\"%s\", \"%s\") = %s" % (
        focus_sentence, sentence1, symmetric_sentence_similarity(focus_sentence, sentence1)))
a = get_tuples_textblob_sentences(sentence1)
b = get_tuples_textblob_sentences(focus_sentence)
print("Jaccard: {}   Cosine: {}".format(jaccard_distance(a,b), cosine_similarity_ngrams(a,b)))



 #################################################### """

""" 
import datetime
y = datetime.datetime.utcnow()
x = datetime.datetime.utcnow()+datetime.timedelta(hours=5.5)

ts = x - y
print(ts)
 """
