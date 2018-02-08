import re, parsing
from geotext import GeoText

### CLEAN/PARSE INFO, THEN ADD IT TO DICTIONARY ###
def add_pair_to_dict(pair, d):
    if pair[0] == 'name':
        d['title'] = pair[1]
    elif re.match('directors?', pair[0]):
        d['director'] = parsing.string2list(pair[1])
    elif re.match('producers?', pair[0]):
        d['producer'] = parsing.string2list(pair[1])
    elif pair[0] == 'starring':
        d['starring'] = parsing.string2list(pair[1])
    elif pair[0] == 'runtime':
        # runtimes require special parsing to convert to minutes
        d['runtime'] = parsing.string2time('='.join(pair[1:]))
    elif pair[0] == 'country':
        d['country'] = parsing.string2list(pair[1])
    elif pair[0] == 'language':
        d['language'] = parsing.string2list(pair[1])

### FIND INFOBOX AND EXTRACT INFORMATION ###
def infobox(pagetext, d):
    if re.search('Infobox', pagetext):
        # infoboxes occur in double curly brackets. regexes may
        # not be sufficient for infobox extraction.
        bracket_parsed = parsing.parse_brackets(pagetext)
        infobox = [i for i in bracket_parsed if 'Infobox' in str(i)][0]
        # infobox lines are split by whitespace
        infobox = re.split(r'\n\|\s*', parsing.flatten(infobox))
        for line in infobox:
            infopair = re.split(r'\s*=\s*', parsing.flatten(line)) #split each infobox line by '=' delimiter
            add_pair_to_dict(infopair, d)

### FINISH CLEANING PAGE TEXT FOR 'TEXT' FIELD ###
def text(pagetext, d):
    # text fields do not contain infoboxes
    bracket_parsed = parsing.parse_brackets(pagetext)
    text = [line for line in bracket_parsed if type(line) != list]
    # clean whitespace and wiki markup from text
    text = [l.strip() for l in text]
    text = ''.join(text)
    text = re.sub('\=+', '\n', text)
    text = re.sub('\n{2,}', '\n\n', text)
    text = parsing.remove_links(text)
    text = re.sub(r'(References|External [Ll]inks).*','',text,flags=re.DOTALL)
    text = re.sub(r'\{\|.*?\|\}', '', text, flags=re.DOTALL)
    d['text'] = text

### SEARCH PAGE TEXT FOR PREVIOUSLY UNFILLED FIELDS ###
def unfound(key, pagetext, d):
    values = None
    # For actors, check 'Cast' section, look for sentence about 'stars', then look for names in parentheses
    if key == 'starring':
        if re.search(r'Cast ?=+', pagetext):
            cast = re.findall(r'Cast ?\=+.*?\=\=', pagetext, re.DOTALL)[0][6:-1]
            cast = [i.strip('*= \n').split(' as ')[0] for i in cast.split('\n*')]
        else:
            cast = re.split(r'(?:stars |, and | and |,)', ''.join(re.findall(r'stars (?:(?:[A-Z][a-z\.]+ ?)+(?: as |, and |, | and |\.))+', pagetext)))
            cast = [i.split(' as ')[0].strip() for i in cast]
        cast = [i for i in cast if i != '']
        if len(cast) == 0:
            if re.search('Plot ?=+', pagetext):
                plot = re.findall(r'Plot ?\=+.*?\=\=', pagetext, re.DOTALL)[0]
                cast = [i[1:-1] for i in re.findall(r'\((?:[A-Z][a-z\.]+ ?)+\)', plot)]
        values = cast
    # For people, look for sentences containing keywords followed by Name Case words.
    elif key in ['producer', 'director']:
        if key=='producer':
            sents = re.findall(r'\produced (?:by|under) .*?\.', pagetext)
        if key=='director':
            sents = re.findall(r'\directed by .*?\.', pagetext)
        for sent in sents:
            values = re.findall(r'(?:[A-Z][a-z\.]+ ?)+', sent)
    # For settings, look in the plot for place names (GeoText) and time words.
    elif key in ['location','time']:
        if key=='location':
            if re.search('Plot ?=+', pagetext):
                plot = re.findall(r'Plot ?\=+.*?\=\=', pagetext, re.DOTALL)[0]
                values = GeoText(plot).cities
                values.extend(GeoText(plot).country_mentions.keys())
                # filter out character names by checking the 'Cast' section
                if re.search(r'Cast ?=+', pagetext):
                    character_names = re.findall(r'Cast ?\=+.*?\=', pagetext, re.DOTALL)[0][6:-1]
                    values = [v for v in values if v not in character_names]
        elif key=='time':
            if re.search('Plot ?=+', pagetext):
                plot = re.findall(r'Plot ?\=+.*?\=\=', pagetext, re.DOTALL)[0]
                time_regex = (r"[0-9]+(?:st|nd|rd|th) [Cc]entury"
                              "|(?:Jan(?:uary|\.)?|Feb(?:ruary|\.)?|Mar(?:ch|\.)?|Apr(?:il|\.)?|May|Jun(?:e|\.)?"
                                  "|Jul(?:y|\.)?|Aug(?:ust|\.)?|Sept(?:ember|\.)?|Oct(?:ober|\.)?|Nov(?:ember|\.)?"
                                  "|Dec(?:ember|\.)?)? ?(?:[1-3]?[0-9](?:st|nd|rd|th)?\,? )?[1-2][0-9][0-9][0-9]")
                values = [v for v in re.findall(time_regex, plot) if not re.search('201[78]', v)] # films taking place in 2017-18 tend not to specify year
    # Add found values to dictionary
    if values != None and values != []:
        values = [v.strip() for v in list(set(values)) if v != '']
        d[key] = values
