"""
Carmi Rothberg
Assignment 2: Building a Corpus
"""

### IMPORTS ###
import re, json
import parsing, extract
from wikitools import wiki, category

### GET WIKI PAGES ###
print('importing pages...')
wikiobj = wiki.Wiki("https://en.wikipedia.org/w/api.php")
wikicat = category.Category(wikiobj, title = "2017_films")
wikipages = wikicat.getAllMembers()
print('pages imported...')

### EXTRACT INFORMATION FROM A PAGE ###
def page2dict(page):
    ### SETUP ###
    d = {'title': None, 'director': None, 'producer': None, 'starring': None, 'runtime': None, 'country': None, 'language': None, 'time': None, 'location': None, 'text': None}
    ### PRELIMINARY DATA ###
    title = re.sub(r'\s*\((2017)?\s*film\)\s*', '', str(page.title.encode('utf8'))) #guess film title from page title
    #print('\t'+title)
    d['title'] = title
    categories = [c[9:] for c in page.getCategories()]
    d['categories'] = categories
    ### DATA FROM PAGE TEXT ###
    pagetext = parsing.remove_html(page.getWikiText()) #clean page text
    # get as much as possible from infobox #
    extract.infobox(pagetext, d)
    # get plain page text #
    extract.text(pagetext, d)
    # search text for any unfound information #
    pagetext = parsing.remove_links(pagetext)
    for key in d.keys():
        if not d[key]:
            extract.unfound(key, pagetext, d)
        if type(d[key])==list:
            if len(d[key])==1:
                d[key] = d[key][0]
    return d

### POPULATE DICTIONARY FROM ALL PAGES ###
allpages = {} #dictionary to fill with all pages' information
for i in range(len(wikipages)-7): #exclude the final 7 wikipages, which are subcategories
    if i%50 == 0:
        print(str(100*i/len(wikipages)) + '% done...')
    pageinfo = page2dict(wikipages[i])
    allpages[i] = pageinfo

### DUMP TO JSON ###
f = open('2017_movies.json', 'w')
json.dump(allpages, f, encoding='utf8')
f.close()
