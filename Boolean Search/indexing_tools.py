print('importing nltk...')
import nltk
porter = nltk.stem.porter.PorterStemmer() #stemmer (Porter)
snowball = nltk.stem.snowball.SnowballStemmer('english') # stemmer (Snowball)
lemmatizer = nltk.stem.WordNetLemmatizer() #lemmatizer (WordNet)
print('imported!')

def sent_split(text):
    return nltk.sent_tokenize(text)

def tokenize(text):
    return nltk.word_tokenize(text)

def get_stem(word):
    return porter.stem(word) # other options are below, but Porter Stemmer is effective and not too time-costly
    #return snowball.stem(word)
    #return lemmatizer.lemmatize(word)
