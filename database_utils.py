import re
import pprint
import json

def dedup_array(array):
    res = []
    for name in array:
        if name not in res:
            res.append(name)
    return res

def dedup_dict(tag_dict):
    junk = []
    for key in tag_dict.keys():
        overlap, main = find_overlap(key, tag_dict)
        if overlap:
            tag_dict[main].extend(overlap)
            junk.extend(overlap)
    print("Duplicate tags found and will be deleted: " + str(junk))
    for entry in junk:
        tag_dict.pop(entry)
    return tag_dict

def find_overlap(key_isdup, dict):
    overlap = []
    max_syn = len(dict[key_isdup])
    main = key_isdup
    for key in dict.keys():
        if key_isdup in dict[key]:
            overlap.append(key_isdup)
            if len(dict[key]) > max_syn:
                main = key
                max_syn = len(dict[key])
    return overlap, main

def remove_fandom(char):
    return re.sub('\(.*\)', '', char).strip()

def split_ship(ship_string, charlist):
    ship_res = []
    if ('/' in ship_string):
        ship_spl = ship_string.split('/')
        if len(ship_spl) > 1:
            ship_res = [filter_name(x.strip(), charlist) for x in ship_spl]
    else:
        ship_spl = ship_string.split('&')
        if len(ship_spl) > 1:
            ship_res = [filter_name(x.strip(), charlist) for x in ship_spl]
    if len(ship_res) > 1:
        ship_res.sort()
    return ship_res

def dedup_char_fandom(d):
    junk = []
    for char in d:
        clean_char = remove_fandom(char)
        if clean_char != char and clean_char in d:
            bucket = d[char]
            d[clean_char].extend(bucket)
            junk.append(char)
    for j in junk:
        d.pop(j)
    new_d = {}
    for char in d:
        new_d[remove_fandom(char)] = d[char]
        new_d[remove_fandom(char)].append(char)
    return new_d

def ships_to_chars(d):
    for key in d.keys():
        for ship in  d[key]['relationships']:
            d[key]['characters'].extend([x.strip() for x in ship.split('/')])
    return d

def dedup_ship_fandom(d, charlist):
    junk = []
    for ship in d:
        clean_ship = remove_fandom(ship).replace(' /', '')
        if clean_ship != ship and clean_ship in d:
            bucket = d[ship]
            d[clean_ship].extend(bucket)
            junk.append(ship)
    print(junk)
    for j in junk:
        d.pop(j)
    new_d = {}
    for ship in d:
        splitted_ship = split_ship(ship, charlist)
        if 'junk' not in splitted_ship:
            new_d[str(splitted_ship)] = d[ship]
            new_d[str(splitted_ship)].append(ship)
    return new_d


# TODO: Lift casefold from this loop. Make comparison more efficient
def filter_name(name, d):
    casefold_name = name.casefold()
    for key in d.keys():
        casefold_list = [x.casefold() for x in d[key]]
        if casefold_name in casefold_list or casefold_name == key.casefold():
            return key
    return 'junk'

def process_dict(d):

    dedup_dict(d)
    print(d)
    # dedup(array)
    # filter_name()
