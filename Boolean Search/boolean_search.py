"""
boolean_search.py
author: 

Students: Modify this file to include functions that implement 
Boolean search, snippet generation, and doc_data presentation.
"""
from boolean_index import NewIndex, ShelvedIndex
from indexing_tools import sent_split, tokenize, get_stem
print('importing flask...')
from flask import Markup
print('flask imported!')

index = ShelvedIndex('index_rothberg_positional.dbm') #open a shelved index

### SEARCH FOR IDS MATCHING A QUERY ###
def search(query, query_type):
        """Return a list of movie ids that match the query."""
        if query_type == 'AND':
                if index.positional: #rank positional searches by term frequency
                        if len(query.split()) == 1:
                                return sorted(index.AND(query.split()), key=lambda result: -len(result[1]))
                        else:
                                return sorted(index.AND(query.split()), key=lambda result: -sum([len(term_hits) for term_hits in result[1]]))
                else: #no order necessary for non-positional searches
                        return index.AND(query.split())
        elif query_type == 'OR':
                if index.positional: #rank positional searches by term frequency
                        return sorted(index.OR(query.split()), key=lambda result: -len(result[1]))
                else: #no order necessary for non-positional searches
                        return index.OR(query.split())
        elif query_type == 'PHRASE':
                if index.positional: #rank positional searches by term frequency
                        return index.PHRASE(query.split())
                else: #back off to conjunctive search for non-positional indices
                        return index.AND(query.split())

### FIND QUERY TERMS NOT IN THE INDEX ###
def get_unknown_terms(query):
        unks = []
        for q in query.split():
                if index.get_postings(q) == []:
                        unks.append(q)
        return unks

### EXTRACT QUERY INFO FROM STRING ###
def parse_query(query):
        """Given a string, return a list of stopwords, a stopword-free query, and a query type"""
        if query == '':
                return '', '', None
        query_type = query.split()[0]
        if query_type == 'AND:':
                return remove_stopwords(query[5:])[0], remove_stopwords(query[5:])[1], 'AND'
        elif query_type == 'OR:':
                return remove_stopwords(query[4:])[0], remove_stopwords(query[4:])[1], 'OR'
        elif query_type == 'PHRASE:':
                return query[8:], [], 'PHRASE'
        return remove_stopwords(query)[0], remove_stopwords(query)[1], 'AND'

### SPLIT QUERY INTO STOPWORDS AND NON-STOPWORDS ###
def remove_stopwords(query):
        skipped = []
        searched = ''
        for q in tokenize(query):
                if get_stem(q) in index.stopwords:
                        skipped.append(q)
                else:
                        searched += q+' ' #stopword-free query
        return searched, [str(sw) for sw in skipped]

### SEARCH CORPUS FOR MOVIE ID ###
def get_movie_data(doc_id):
        """
        Return data fields for a movie.
        Your code should use the doc_id as the key to access the shelf entry for the movie doc_data.
        You can decide which fields to display, but include at least title and text.
        """
        movie_object = {"title": index.corpus[doc_id]["title"],
                                        "director": index.corpus[doc_id]["director"],
                                        "location": index.corpus[doc_id]["location"],
                                        "text": Markup(index.corpus[doc_id]["text"].replace('\n', '<br>'))
                                        }
        return(movie_object)

### FIND TERM FREQUENCY IN A GIVEN SENTENCE ###
def get_hits(sent, terms):
        hits = 0
        for word in sent.split():
                if get_stem(word.strip('.,\'"!()')) in terms:
                        hits+=1
        return hits

### CREATE A SNIPPET GIVEN A DOCUMENT AND A QUERY ###
def movie_snippet(doc_id, query):
        """
        Return a snippet for the results page.
        Needs to include a title and a short description.
        Your snippet does not have to include any query terms, but you may want to think about implementing
        that feature. Consider the effect of normalization of index terms (e.g., stemming), which will affect
        the ease of matching query terms to words in the text.  
        """
        title = index.corpus[doc_id[0]]['title']
        sents = sent_split(index.corpus[doc_id[0]]['text'])
        query_terms = [get_stem(word.strip('.,\'"!()')) for word in query.split()]
        snippet_hits = (sents[0], get_hits(sents[0], query_terms)) # default to first sentence as snippet
        for sent in sents: # if another sentence contains more query terms, use that as the snippet, instead
                sent_hits = get_hits(sent, query_terms)
                if sent_hits > snippet_hits[1]:
                        snippet_hits = (sent, sent_hits)
        snippet = snippet_hits[0].split()[:100] # limit snippet length to 100 words
        snippet_string = ''
        for word in snippet:
                if get_stem(word.strip('.,\'"!()')) in query_terms:
                        snippet_string += Markup("<strong>"+word+"</strong> ") # emphasize query terms in snippet
                else:
                        snippet_string += word+" "
        return (doc_id[0], title, snippet_string)
