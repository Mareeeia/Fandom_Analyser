import re

def dedup_array(array):
    res = []
    for name in array:
        if name not in res:
            res.append(name)
    return res

def dedup_dict(tag_dict):
    for key in tag_dict.keys():
        overlap, main = find_overlap(key, tag_dict)
        if not overlap.empty():
            tag_dict[main] = tag_dict[main].appendall[overlap]
            tag_dict.remove(overlap)

def find_overlap(key_isdup, dict):
    overlap = []
    max_syn = len(dict[key_isdup])
    main = ''
    for key in dict.keys():
        if key_isdup in dict[key]:
            overlap.append(key)
            if len(dict[key]) > max_syn:
                main = key
                max_syn = len(dict[key])
    return overlap, main

def remove_fandom(char):
    return re.sub('\(.*\)', '', char)

def split_ship(ship_string):
    if ('/' in ship_string):
        ship_spl = ship_string.split('/')
        if len(ship_spl) > 1:
            ship_res = [filter_name(x) for x in ship_spl]
    else:
        ship_spl = ship_string.split('&')
        if len(ship_spl) > 1:
            ship_res = [filter_name(x) for x in ship_spl]
    return ship_res.sort()


def filter_name(name, d):
    for key in d.keys():
        if name in d[key]:
            return key

def process_dict(d):

    dedup_dict()
    dedup(array)
    filter_name()
