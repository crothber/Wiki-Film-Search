import re

### FLATTEN A LIST TO A STRING ###
# advantage over built-in 'str()' method: preserves unicode in nested lists
def flatten(l):
    if type(l) == list:
        for i in range(len(l)):
            l[i] = flatten(l[i])
        l = ' '.join(l)
    return l

### CONVERT A STRING CONTAINING BRACKETS INTO AN EQUIVALENT LIST ###
def parse_brackets(s):
    l = []
    depth = 0
    current = l
    i = 0
    while i < len(s):
        char = s[i]
        if i < len(s)-1:
            char1= s[i+1]
        else:
            char1 = ''
        if char == '{' and char1 == '{': # '{{' moves in a layer
            depth += 1
            current.append([])
            current = l
            for j in range(depth):
                current = current[-1]
            i += 1
        elif char == '}' and char1 == '}': # '}}' moves out a layer
            depth -= 1
            current = l
            for j in range(depth):
                current = current[-1]
            i += 1
        else: # no change in depth, just add character
            if len(current) == 0:
                current.append(char)
            elif type(current[-1]) == list:
                current.append(char)
            else:
                current[-1] += char
        i += 1
        #if depth<0:
            #print("ERROR: brackets not balanced")
            #return l
    return l

### GENERAL REGEXES FOR HTML MARKUP ###
def remove_html(s):
    s = re.sub(r"'{2,}", '', s)
    s = re.sub(r"\{\{cite.*?\}\}", '', s)
    s = re.sub(r"<br\s?/?>", '\n', s)
    s = re.sub(r"\<ref.*?\<\/ref\>", '', s)
    s = re.sub(r"\<.*?\>", '', s)
    s = re.sub(r"http.*?[ \n]", '', s)
    s = re.sub(r"\&nbsp", '', s)
    s = re.sub(r"\(\)", '', s)
    s = re.sub(r"File\:.*?\n", '\n', s)
    s = re.sub(r"ub1", '', s)
    return s

### REMOVE LINKS FROM A STRING ###
def remove_links(s):
    links = re.findall(r'\[\[.*?\]\]', s)
    for link in links:
        s = s.replace(link, link[2:-2].split('|')[-1]) # remove link text, keep display text
    s = re.sub(r'[\[\]]', '', s) # remove all brackets
    return s.strip().decode('utf8', errors='ignore')

### CONVERT A STRING TO A 'MINUTES' INTEGER ###
def string2time(s):
    if s == '':
        return None
    else:
	time = 0
        mins = re.findall(r'm=[0-9]+|[0-9]+ ?[Mm]', s)
        if len(mins)>0:
            time += int(''.join([c for c in mins[0] if c.isdigit()]))
        hrs = re.findall(r'h=[0-9]+|[0-9]+ ?[Hh]', s)
        if len(hrs)>0:
            time += 60*int(''.join([c for c in hrs[0] if c.isdigit()]))
    return time

### CLEAN A STRING AND SPLIT IT INTO A LIST ###
def string2list(s):
    s = remove_links(s)
    s = re.sub(r'(unbulleted list|[Pp]lain( ?)list)|\{|\}|\*|ub1','',s) # remove list markup
    s = re.sub(r'[Cc]o ?-? ?[Pp]roducer\:?','',s) # consider co-producers to be producers
    s = re.sub(r'\n','|',s) # keep delimiters a consistent '|'
    l = re.split('\|+', s) # split by '|' delimiter
    l = [i.strip() for i in l if i!='']
    if len(l)>0:
        return l
    else:
        return
