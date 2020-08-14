import requests
import logging
import string
import re


try:
    from __app__.assets import area as ar
    from __app__.assets import character as ch
    from __app__.assets import exclude as exc
    from __app__.assets import specials as sp
    from __app__.assets import landtag as lt
    from __app__.assets import ambiguous as am
except Exception as e:
    logging.info('[INFO] Helper: Using local imports.')
    import assets.area as ar
    import assets.ambiguous as am
    import assets.character as ch
    import assets.exclude as exc
    import assets.specials as sp
    import assets.landtag as lt

# Table to efficiently remove punctuations
table = str.maketrans({key: None for key in string.punctuation if key is not '-'})

# Lookup objects
dict_area = ar.obj
dict_ambg = am.obj
dict_char = ch.obj
dict_spec = sp.obj
list_excl = exc.obj
list_landtag = lt.obj

##############################
##### Input Processing
##############################

def score_luis(text, appid, key, location='westeurope'):
    """Get results from LUIS: license plate extraction"""
    headers = {
        'Ocp-Apim-Subscription-Key': key,
    }
    params ={
        'q': text,
        'timezoneOffset': '0',
        'verbose': 'false',
        'spellCheck': 'false',
        'staging': 'false',
    }

    try:
        r = requests.get(f'https://{location}.api.cognitive.microsoft.com/luis/v2.0/apps/{appid}',
                        headers=headers, params=params)
        r = r.json()
    except Exception as e:
        logging.info(f"[ERROR] LUIS encountered an issue. {e}")
        r = None
    return r

##############################
##### LP Extraction
##############################

def validate_reduce(phrase, letter, start, stop):
    """Validate single letter word comparisons"""
    if len(letter) == 1:
        if letter != phrase[start:stop].strip().split()[2][0]:
            letter = phrase[start:stop].strip().split()[2][0]
    return letter

def reduce_lp(phrase):
    """Reduce License Plate"""
    
    # Reduce characters
    for key in dict_spec.keys():
        phrase = phrase.replace(key, dict_spec[key])
    phrase = ' '.join([str(dict_char.get(i, i)) for i in phrase.translate(table).split() if i not in list_excl])

    # Search for area code
    for key in dict_area:
        if (' ' + key + ' ') in (' ' + phrase + ' '):
            match  = re.search(key, phrase)
            start  = match.span(0)[0]
            stop   = match.span(0)[1]
            phrase = phrase[start:]
            break
    
    ##TODO: bug for rostock - since multiple options. 
    ##solution
    #create list of multiple options, special check for those
    for key in dict_ambg:
        if (' ' + key + ' ') in (' ' + phrase + ' '):
            ambig = True
            break
        else:
            ambig = False

    # Replace general "wie"-comparisons
    while True:
        match = re.search(r'(\s|^)([a-z]{1,3}) (wie|für|von|wir) \w+', phrase)
        if match:
            start = match.span(0)[0]
            stop = match.span(0)[1]
            letter = validate_reduce(phrase, phrase[start:stop].strip().split()[0], start, stop)
            phrase = phrase[:start] + ' ' + letter + phrase[stop:]
        else:
            break

    # Replace letter multiplication
    while True:
        match = re.search(r'(doppel [a-z])', phrase)
        if match:
            start=match.span(0)[0]
            stop=match.span(0)[1]
            letter = 2 * phrase[start:stop][-1]
            phrase = phrase[:start] + letter + phrase[stop:]
        else:
            break

    # Replace number multiplication
    while True:
        match = re.search(r'(doppel [0-9])', phrase)
        if match:
            start=match.span(0)[0]
            stop=match.span(0)[1]
            letter = 2 * phrase[start:stop][-1]
            phrase = phrase[:start] + letter + phrase[stop:]
        else:
            break

    # Replace number multiplication
    while True:
        match = re.search(r'([1-9] mal( die)? [0-9])', phrase)
        if match:
            start=match.span(0)[0]
            stop=match.span(0)[1]
            number = int(phrase[start:stop][0:1]) * phrase[start:stop][-2:].strip()
            phrase = phrase[:start] + number + phrase[stop:]
        else:
            break

    # Replace letter multiplication
    while True:
        match = re.search(r'([1-9] mal( die)? [a-z])', phrase)
        if match:
            start=match.span(0)[0]
            stop=match.span(0)[1]
            char = int(phrase[start:stop][0:1]) * phrase[start:stop][-2:].strip()
            phrase = phrase[:start] + char + phrase[stop:]
        else:
            break

    # Letter number split
    entity_reduced = list(phrase)
    entity_str = []
    for e in entity_reduced:
        if e.isdigit():
            break
        entity_str.append(e)
    entity_num = ''.join([n for n in entity_reduced[len(entity_str):] if n.isdigit()])
    entity_str = (''.join(entity_str)).split()
    
    # Extract electric and histroical vehicle LPs
    entity_extra = ''
    if entity_reduced[-1] in ['e','h','c']:
        entity_extra = entity_reduced[-1]

    # Check for incomplete LP
    if entity_num == '':
        entity_extra = ''
    
    # Remove noise from reduced
    phrase = phrase.replace(" ", "")

    return entity_str, entity_num, entity_extra, phrase, ambig

def area_lookup(area):
    """Loockup full area name from area code"""
    try:
        area_full = next(k for k, v in dict_area.items() if v == area)
    except Exception as e:
        area_full = 'FALSE'
    return area_full

def check_area_ngram(entity_split, n):
    """Search for ngram areas"""
    if n == 1:
        area_split = entity_split
        letter_replace = None
    else:
        area_split = [' '.join(entity_split[:n])]
        letter_replace = ' '.join(area_split)
    area = ' '.join([str(dict_area.get(i, i)) for i in area_split if i not in list_excl and i in dict_area]) 
    return area_split, letter_replace, area

def multi_area_lookup(entity, length):
    """Lookup for multiple area options"""
    # Extract area options
    areas_full = []
    letters = []
    areas = []
    if length < 4:
        _areas = [entity[:1], entity[:2], entity[:3]]
    elif length == 4:
        _areas = [entity[:2], entity[:3]]
    elif length == 5:
        _areas = [entity[:3]]
    else:
        areas_full = ['UNKNOWN']
        _areas = areas
        letters = [entity]
    
    # Lookup areas
    for a in _areas:
        _area_full = area_lookup(a)
        if _area_full != 'FALSE':
            areas.append(a)
            areas_full.append(_area_full)
            letters.append(entity[len(a):])
        
    if len(areas_full) == 0:
        areas_full.append('FALSE')
        letters.append(entity)
    
    return letters, areas, areas_full

def get_lp_area(entity, entity_split):
    """Extract area code"""
    # N-gram Area Lookup
    area = []
    ngram = 4
    while len(area) == 0 and ngram != 0:
        ## Fetch areas with n-gram
        area_split, letter_replace, area = check_area_ngram(entity_split, ngram)
        ## Special treatment for unigram
        if len(area) != 0 and ngram == 1:
            area_len = len(area.split(" ")) - 1
            if area_len > 0:
                area = area.split(" ")[0]
                entity_split = entity_split[area_len:]
                area_split = area_split[area_len:]
        ngram -= 1
    entity_join = ''.join(entity_split)
    entity_len = len(entity_join)
    
    # Area post processing & validation
    if len(area) > 0:
        area_full = ' '.join([i for i in area_split if i not in list_excl and i in dict_area])
        if letter_replace is not None:
            letter = str(' '.join(entity_split)).replace(letter_replace, '')
            letter = ' '.join([i for i in letter.split() if i not in list_excl])
        else:
            letter = ' '.join([i for i in entity_split if i not in list_excl and i not in dict_area])
    
    elif '-' in entity_split:
        area = entity_join.split('-')[0]
        area_full = area_lookup(area)
        if area_full == 'FALSE':
            area = ''
            letter = entity_join
        else:
            letter = entity_join.replace(area,'',1).replace("-","")

    else:
        ## Area detection for multiple areas
        letter, area, area_full = multi_area_lookup(entity_join, entity_len)

    return letter, area, area_full

def format_lp(area, letter, number, extra='', lp_type='standard'):
    """Merge and format license plate"""
    if lp_type == 'diplomat':
        return f'{area}-{letter}-{number}{extra}'.replace(' ','').upper()
    elif lp_type == 'bundeswehr':
        return f'{area}-{letter}{extra}'.replace(' ','').upper()
    else:
        return f'{area}-{letter}{number}{extra}'.replace(' ','').upper()

def validate_lp(lp, lp_type='standard'):
    """Final validation of formatted license plate"""

    if lp_type == 'diplomat':
        regex = r'^0\-[0-9]{1,2}\-[0-9]{1,3}(E|H|C)?$'
    elif lp_type == 'bundeswehr':
        regex = r'^Y\-[0-9]{1,6}(E|H|C)?$'
    elif lp_type == 'bp':
        regex = r'^BP\-[0-9]{1,5}(E|H|C)?$'
    elif lp_type in list_landtag:
        regex = r'^[A-ZÄÖÜ]{1,3}\-(([A-Z]{1,2}[0-9]{1,4})|([0-9]{1,6}))(E|H|C)?$'
    else:
        regex = r'^[A-ZÄÖÜ]{1,3}\-[A-Z]{1,2}[0-9]{1,4}(E|H|C)?$'
    
    if re.match(regex, lp):
        valid = True
    else:
        valid = False
    return valid

def get_lp_standard(entity, string, number, extra):
    """Handling of standard (common) license plates"""
    # Get LP Area
    letter, area, area_full = get_lp_area(entity, string)
    # Delete duplicates in letter combination
    if isinstance(letter, str):
        if len(letter.replace(" ", "")) == 4: 
            letter = letter.replace(" ", "")
            if letter[0] == letter[2] and letter[1] == letter[3]:
                letter = letter[0] + letter[1]

    # Prepare for next steps
    if isinstance(area, list):
        number = [number for n in area]
    else:
        letter, area, area_full, number = [letter], [area], [area_full], [number]
    
    # Output
    _lp = []
    _split = []
    _valid = []
    for a, l, n, af in zip(area, letter, number, area_full):

        # Format LP
        lp_formatted = format_lp(a, l, n, extra)
        _lp.append(lp_formatted)

        # Validate LP
        v = validate_lp(lp_formatted, lp_type=a)
        _valid.append(v)

        if not v:
            if len(l) > 2:
                l = ''
            if len(n) > 4:
                n = ''
        
        _split.append(dict(
            area_full   =   af,
            area        =   a,
            letter      =   l,
            number      =   n, 
            extra       =   extra
            ))
    
    # Only pass valid LPs
    lp = []
    split = []
    valid = []
    if any(_valid) != all(_valid):
        for _v, _l, _s in zip(_valid, _lp, _split):
            if _v:
                lp.append(_l)
                split.append(_s)
                valid.append(_v)
    else:
        lp = _lp
        split = _split
        valid = _valid

    return lp, split, all(valid)

def get_lp_special(entity, extra, reduced):
    """Handling of special license plate types, such as diplomat"""
    # Check for missing connection
    if reduced[1] != '-':
        reduced = reduced[0] + '-' + reduced[1:]
    
    third = ''
    if reduced[0] == '0':
        lp_type = 'diplomat'
        try:
            first = reduced[0]
            second = reduced.split('-')[1]
            third = ''.join([n for n in reduced.split('-')[2] if n.isdigit()])
        except IndexError:
            first = reduced[0]
            second = ''.join([n for n in reduced.split('-')[1] if n.isdigit()])

    elif reduced[0] == 'y':
        lp_type = 'bundeswehr'
        first = reduced[0]
        second = ''.join([n for n in reduced[1:] if n.isdigit()])
    
    # Create LP
    lp = [format_lp(first, second, third, extra, lp_type)]

    # Validate LP
    valid = validate_lp(lp[0], lp_type)

    # Create split
    split = [dict(
        area_full = lp_type,
        area = first,
        letter = '',
        number = second + third,
        extra = extra
    )]

    return lp, split, valid

def get_lp(ori, entity):
    """Orchestrate license plate formatting and validation"""

    # Translate and clean input
    string, number, extra, reduced, ambig = reduce_lp(entity) 

    # Check for LP type
    if (len(string) < 1) or (string[0] == 'y'):
        ## Treat as special LP
        lp, split, valid = get_lp_special(entity, extra, reduced)
    else:
        ## Treat as standard LP
        lp, split, valid = get_lp_standard(entity, string, number, extra)

    return entity, lp, split, valid, ambig

##############################
##### Output Processing
##############################

def format_output(query, lp, split, valid, start, end, ambig):
    """Format the request response of the Azure Function"""
    out = []
    cpl_query = query
    for l, s in zip(lp, split):
        lps = dict()
        if not valid:
            lps['entity'] = ''
        else:
            lps['entity'] = l
            cpl_query = cpl_query[:start] + lps.get('entity') + cpl_query[end+1:]                        
        lps['type'] = 'licensePlate'
        lps['entitySplit'] = dict(
            fullAdminDistrict = s.get('area_full'),
            adminDistrict = s.get('area'),
            letterCombination = s.get('letter'),
            numberCombination = s.get('number'),
            extra = s.get('extra'),
            ambiguous = ambig
        )
        out.append(lps)
    return out, cpl_query