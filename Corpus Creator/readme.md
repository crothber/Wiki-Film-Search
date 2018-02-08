# Building a Corpus
#### Carmi Rothberg
## Description
This program extracts pages from Wikipedia and identifies key information from the pages. Specifically, the program searches for pages from the category ‘2017 films’ and uses Wikipedia’s ‘Infobox’ structure, along with a number of text-processing heuristics, to identify fields such as title, director, and setting.
## Dependencies
The submitted code is written for Python 2.7. Python code should run identically under OSX and Windows.
Required Python modules are re, json, wikitools (pip install wikitools), and geotext (pip install geotext).
## Build Instructions
Not applicable.
## Run Instructions
This program can be run in Python using the file run.py. Internet connection is required.
## Modules
### run.py
The main module goes through the Wikipedia ‘2017 films’ category and creates a dictionary object for each page, using the extract and parsing modules.
First, the program will identify the film title from the page’s ‘title’ field, as well as the page’s categories from the ‘categories’ field. The program will then attempt to populate the dictionary with the page’s infobox, if one can be found. Next, the page’s text is cleaned, added to the page’s dictionary, and searched for more information.
Each dictionary is subsequently added to a larger dictionary (a ‘dictionary of dictionaries’). The completed dictionary of dictionaries is then dumped to a json file. The json output is encoded in utf8 to preserve special characters.
### parsing.py
This file contains methods to clean and parse text.
The flatten() and parse_brackets() methods convert between strings and lists. This is useful in extracting infoboxes and changing delimiters.
The remove_html() and remove_links() methods clean unnecessary markup from the pages. This makes for more readable text and clears items that might confuse field identification.
The string2time() and string2list() methods clear additional markup from identified fields and convert them into appropriate forms for storing (i.e., times are converted to minute integers, and lists of names are converted to list objects).
### extract.py
This is where most of the heavy lifting is done.
The infobox() method uses parse_brackets to identify a page’s infobox, then uses flatten() and regexes to split the infobox into appropriate key/value pairs.
The text() method uses parse_brackets to identify plain text in a page, then uses regexes to remove markup.
The unfound() method uses geotext and regexes to identify previously unfound information. For example, time setting can be found by searching for dates or centuries within a page’s ‘Plot’ field, place setting can be found by searching for geotext in the ‘Plot’ field and filtering out character names found in the ‘Cast’ list, and people can be found by looking for Name Case phrases that appear after key phrases (like ‘produced by’ or ‘starring’) in a sentence.
## Testing:
The program was run on all pages in the Wikipedia ‘2017 films’ category. In addition to manually reviewing samples of the output, I used Python to scan outputs for missing fields and uncaught markup keywords (like ‘>’s and ‘.com’s).
73.5% of all fields were filled, with what seems to be generally correct information.
