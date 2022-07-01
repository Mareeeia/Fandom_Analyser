import json
import re
import logging
from src.params.folder_params import *


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
        if overlap and main != key:
            tag_dict[main].extend(overlap)
            junk.extend(overlap)
    print("Duplicate items found and will be deleted: " + str(junk))
    for entry in junk:
        if entry in tag_dict.keys():
            tag_dict.pop(entry)
    return remove_empty_tags(tag_dict)


def remove_empty_tags(tag_dict):
    new_dict = {}
    for key in tag_dict.keys():
        if tag_dict[key] != [] or is_main(tag_dict, key):
            new_dict[key] = tag_dict[key]
    return new_dict


def is_main(tag_dict, is_main):
    for key in tag_dict.keys():
        if is_main in tag_dict[key]:
            return False
    return True


def find_overlap(key_isdup, dict):
    overlap = []
    max_syn = len(dict[key_isdup])
    main = key_isdup
    for key in dict.keys():
        if key != key_isdup and (key_isdup in dict[key] or len(set(dict[key_isdup]) & set(dict[key])) > 0):
            overlap.append(key)
            if len(dict[key]) > max_syn:
                main = key
                max_syn = len(dict[key])
    filt_overlap = []
    for entry in overlap:
        if entry != main:
            filt_overlap.append(entry)
    if filt_overlap:
        print(key_isdup)
        print(filt_overlap)
    return filt_overlap, main


def remove_fandom(char):
    return re.sub('\(.*\)', '', char).strip()


def split_ship(ship_string, charlist):
    ship_res = []
    if ('/' in ship_string):
        ship_spl = [remove_fandom(x) for x in ship_string.split('/')]
        if len(ship_spl) > 1:
            ship_res = [filter_name(x.strip(), charlist) for x in ship_spl]
    else:
        ship_spl = [remove_fandom(x) for x in ship_string.split('&')]
        if len(ship_spl) > 1:
            ship_res = [filter_name(x.strip(), charlist) for x in ship_spl]
    if len(ship_res) > 1:
        ship_res.sort()
    return ship_res


def dedup_char_fandom(d):
    d = dedup_dict(d)
    new_d = {}
    for char in d:
        new_d[remove_fandom(char)] = d[char]
        if char != remove_fandom(char):
            new_d[remove_fandom(char)].append(char)
    return new_d


def ships_to_chars(d):
    for key in d.keys():
        for ship in d[key]['relationships']:
            d[key]['characters'].extend([x.strip() for x in ship.split('/')])
    return d


def dedup_ship_fandom(d, charlist):
    d = dedup_dict(d)
    new_d = {}
    for ship in d:
        splitted_ship = split_ship(ship, charlist)
        clean_ship = [remove_fandom(x) for x in splitted_ship]
        if 'junk' not in clean_ship:
            if str(clean_ship) in new_d.keys():
                new_d[str(clean_ship)].extend(d[ship])
            else:
                new_d[str(clean_ship)] = d[ship]
            if str(clean_ship) != ship:
                new_d[str(clean_ship)].extend([ship])
    return new_d


# TODO: Lift casefold from this loop. Make comparison more efficient
def filter_name(name, d):
    casefold_name = name.casefold()
    for key in d.keys():
        casefold_list = [x.casefold() for x in d[key]]
        if casefold_name in casefold_list or casefold_name == key.casefold():
            return key
    return 'junk'


def remove_mentioned(name):
    return name.replace(" - Mentioned", "")


def standardize_char_names(charlist, char_dict):
    result_list = []
    for char in charlist:
        char = remove_fandom(char)
        char = remove_mentioned(char)
        for char_name in char_dict.keys():
            if (char in char_dict[char_name] or char.casefold() == char_name.casefold()) and char not in result_list:
                result_list.append(char_name)
    return result_list


def standardize_tags(taglist, tag_dict):
    result_list = []
    for tag in taglist:
        for tag_name in tag_dict.keys():
            if (tag in tag_dict[tag_name] or tag.casefold() == tag_name.casefold()) and tag not in result_list:
                result_list.append(tag_name)
    return result_list


def standardize_ships(shiplist, ship_dict):
    result_list = []
    for ship in shiplist:
        for ship_name in ship_dict.keys():
            if (ship in ship_dict[ship_name] or ship.casefold() == ship_name.casefold()) and ship not in result_list:
                result_list.append(ship_name)
    return result_list


def process_dict(d, char_dict, tag_dict, ship_dict):
    for work in d.keys():
        d[work]['characters'] = standardize_char_names(d[work]['characters'], char_dict)
        d[work]['tags'] = standardize_tags(d[work]['tags'], tag_dict)
        d[work]['relationships'] = standardize_ships(d[work]['relationships'], ship_dict)
    return d


def combine_tag_files():
    files = os.listdir(ROOT_DIR + FILES_ROOT)
    total_tags_dict: dict = {}
    for filename in files:
        print(filename)
        if "DS_Store" not in filename:
            with open(ROOT_DIR + FILES_ROOT + filename + "/processed/tags.json") as tags:
                tag = json.load(tags)
                total_tags_dict.update(tag)

    with open(ROOT_DIR + COMBINED_TAGS, 'w') as tag_file:
        json.dump(total_tags_dict, tag_file)
