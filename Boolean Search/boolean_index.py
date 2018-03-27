from indexing_tools import sent_split, tokenize, get_stem
from search_tools import intersect, union
import json
import shelve
import timeit

class Index:
    def __init__(self, corpus, index, stopwords, positional):
        self.corpus = corpus
        self.index = index
        self.stopwords = stopwords
        self.positional = positional
    # normalize a word, then look it up in the index
    def get_postings(self, term):
        stem = get_stem(term)
        if str(stem) in self.index:
            return self.index[str(stem)]
        else:
            return []
    # check a word against the stopword set
    def is_stopword(self, word):
        if get_stem(word) in self.stopwords:
            return True
        else:
            return False
    # search for the conjunctions of multiple terms
    def AND(self, terms):
        postings = sorted([self.get_postings(term) for term in terms], key=lambda x: len(x)) #sort postings for fastest intersection
        # intersect a pair, then intersect the next postings list with that intersection
        results = list(postings[0])
        for next_postings in postings[1:]:
            results = intersect(results, next_postings, self.positional)
        return results
    # search for the disjunctions of multiple terms
    def OR(self, terms):
        postings = [self.get_postings(term) for term in terms]
        # join a pair of postings lists, then join the next list to the results of the first conjunction
        results = list(postings[0])
        for next_postings in postings[1:]:
            results = union(results, next_postings, self.positional)
        return results
    # search for phrases in a positional index
    def PHRASE(self, terms):
        if self.positional:
            if len(terms) == 1:
                return self.get_postings(terms[0])
            postings = [self.get_postings(term) for term in terms]
            intersection = list(postings[0])
            for next_postings in postings[1:]:
                intersection = intersect(intersection, next_postings, self.positional)
            results = []
            for doc in intersection:
                if doc[0] not in results:
                    found = True
                    for pos in doc[1][0]: #for each position of the first query term
                        found = True #assume the rest of the query phrase follows
                        for i in range(1, len(terms)): #for each subsequent query term
                            if pos+i not in doc[1][i]: #if the term does not follow in the document, break
                                found = False
                                break
                if found:
                    results.append([doc[0]])
            return results
        else:
            print('ERROR! Phrasal searching is not allowed\nin a non-positional index!')
    def lookup(self, movie_id):
        return self.corpus[movie_id]

class NewIndex(Index):
    def __init__(self, corpus_name, shelf_name, positional=True):

        ### START RECORDING BUILD TIME ###
        start_time = timeit.default_timer()

        ### ESTABLISH VARIABLES ###
        self.index = {}
        self.bonus_index = {'director':{}, 'starring':{},'location':{}}
        self.corpus = json.load(open(corpus_name))
        self.positional = positional

        ### BUILD INDEX ###
        print('building index...')
        for docID in self.corpus.keys(): #for each document...
            text = self.corpus[docID]['title']+' '+self.corpus[docID]['text']
            # TOKENIZE
            tokenized = tokenize(text)
            # STEM
            stemmed = [get_stem(word) for word in tokenized]
            for i in range(len(stemmed)): #for each term in that document...
                token = stemmed[i]
                if self.positional:
                    if token not in self.index: #if the term hasn't been seen at all
                        self.index[token] = [[docID, [i]]] #add the term, the docID, and the loc
                    else:
                        found = False
                        for doc in self.index[token]:
                            if doc[0] == docID: #if the term has been seen in this doc
                                doc[1].append(i)
                                found = True
                                break
                        if not found: #if the term has been seen but not in this doc
                            self.index[token].append([docID, [i]])
                elif not self.positional:
                    if token not in self.index: #if the term hasn't been seen at all
                        self.index[token] = [[docID]] #add the term and the docID
                    elif self.index[token][-1] != [docID]: #if the term has been seen but not in this doc
                            self.index[token].append([docID]) #add the docID to the term postings

        print('index built!')

        ### SET STOPWORDS ###
        print('setting stopwords...')
        self.stopwords = set()
        for term in self.index: #each stem could be a potential stopword
            self.index[term] = sorted(self.index[term], key=lambda x: int(x[0])) #sort each posting list by DocID
            if len(self.index[term]) > len(self.corpus.keys())/3: #stopwords occur in more than 1/3 of all documents
                self.stopwords.add(term)
        print('stopwords set!')

        elapsed = timeit.default_timer() - start_time ### BUILDING IS OVER
        print('Time elapsed: ' + str(elapsed))

        ### SHELVE INDEX FOR LATER USE ###
        print('shelving index...')
        myShelf = shelve.open(shelf_name)
        myShelf['corpus'] = self.corpus
        myShelf['index'] = self.index
        myShelf['stopwords'] = self.stopwords
        myShelf['positional'] = self.positional
        myShelf.close()
        print('shelf complete!')
        ### INITIALIZE BASE CLASS ###
        Index.__init__(self, self.corpus, self.index, self.stopwords, self.positional)

class ShelvedIndex(Index):
    def __init__(self, shelf_name):
        print('opening index...')
        myShelf = shelve.open(shelf_name)
        self.corpus = myShelf['corpus']
        self.index = myShelf['index']
        self.stopwords = myShelf['stopwords']
        self.positional = myShelf['positional']
        myShelf.close()
        Index.__init__(self, self.corpus, self.index, self.stopwords, self.positional)
        print('index opened!')

"""
print('\ntest corpus')
test = NewIndex('test_corpus.json', 'test_corpus.dbm')

print('\nshared positional')
NewIndex('films_corpus_shared.json', 'index_shared_positional.dbm')
# build time: 466.998 seconds (7.8 min)
# file size: 28.3 MB

print('\nrothberg positional')
NewIndex('films_corpus.json', 'index_rothberg_positional.dbm')
# build time: 564.793 seconds (9.5 min)
# file size: 31.5 MB

print('\nshared nonpositional')
NewIndex('films_corpus_shared.json', 'index_shared_nonpositional.dbm', positional=False)
# build time: 213.708 seconds (3.5 min)
# file size: 16.5 MB

print('\nrothberg nonpositional')
NewIndex('films_corpus.json', 'index_rothberg_nonpositional.dbm', positional=False)
# build time: 244.608 seconds (4.0 min)
# file size: 18.4 MB
"""
