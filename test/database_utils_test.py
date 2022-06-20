import json
import os
import unittest

from typing import List

import src.database_utils as utils
import src.extract_data as ext


class test_database_utils(unittest.TestCase):

    def test_dedup_array(self):
        duplicated = ['Vlad', 'Katarina', 'LeBlanc', 'Samira', 'LeBlanc', 'Kled', 'LeBlanc', 'LeBlanc']
        dedup = utils.dedup_array(duplicated)
        assert (dedup == ['Vlad', 'Katarina', 'LeBlanc', 'Samira', 'Kled'])

    def test_dedup_dict(self):
        duplicated = {"cat": ["kitten", "kot", "ket", "purr"],
                      "dog": ["pupper", "doggo", "doge"],
                      "kitte": ["cat", "kot"],
                      "kotato": ["cat"]}
        dedup = utils.dedup_dict(duplicated)
        assert (dedup == {'cat': ['kitten', 'kot', 'ket', 'purr', 'kotato', 'kitte'],
                          'dog': ['pupper', 'doggo', 'doge']})

    def test_find_overlap(self):
        duplicated = {"cat": {"kitten", "kot", "ket", "purr"},
                      "dog": {"pupper", "doggo", "doge"},
                      "kitte": {"cat", "kot"},
                      "kotato": {"cat"}}
        overlap, main = utils.find_overlap("kitte", duplicated)
        assert (overlap == ["cat", "kitte", "kotato"])
        assert (main == "cat")

    def test_remove_fandom(self):
        name = 'cat(cats)'
        fixed = utils.remove_fandom(name)
        assert (fixed == 'cat')

    def test_filter_name(self):
        name = "purr"
        charlist = {'cat': ['kitten', 'kot', 'ket', 'purr', 'kotato', 'kitte'], 'dog': ['pupper', 'doggo', 'doge']}
        new = utils.filter_name(name, charlist)
        assert (new == 'cat')

    def test_split_ship(self):
        ship = 'purr/pupper'
        charlist = {'cat': ['kitten', 'kot', 'ket', 'purr', 'kotato', 'kitte'], 'dog': ['pupper', 'doggo', 'doge']}
        new = utils.split_ship(ship, charlist)
        assert (new == ['cat', 'dog'])

    def test_dedup_char_fandom(self):
        duplicated = {"cat(cats)": ["kitten", "kot", "ket", "purr"],
                      "dog": ["pupper", "doggo", "doge"],
                      "kitte": ["cat", "kot"],
                      "kotato": ["cat"]}
        dedup = utils.dedup_char_fandom(duplicated)
        assert (dedup == {'cat': ['kitten', 'kot', 'ket', 'purr', 'kotato', 'kitte', 'cat(cats)'],
                          'dog': ['pupper', 'doggo', 'doge']})

    def test_dedup_char_fandom_bug(self):
        duplicated = {"cat(cats)": ["kotato"],
                      "kotato": []}
        dedup = utils.dedup_char_fandom(duplicated)
        assert (dedup == {'cat': ['kotato', 'cat(cats)']})

    def test_ships_to_chars(self):
        works = {"story": {"relationships": ["cat/dog"],
                           "characters": ["fish"]}}
        new_works = utils.ships_to_chars(works)
        assert (new_works["story"]["characters"] == ["fish", "cat", "dog"])

    def test_dedup_ship_fandom(self):
        shiplist = {"cat(cats)/dog(dogs)": ['kitte/doge', 'purr/doggo'], 'doggo/doggo': [], 'pupper/cat(cats)': []}
        charlist = {'cat': ['kitten', 'kot', 'ket', 'purr', 'kotato', 'kitte'], 'dog': ['pupper', 'doggo', 'doge']}
        dedup_ships = utils.dedup_ship_fandom(shiplist, charlist)
        assert (dedup_ships == {
            "['cat', 'dog']": ['kitte/doge', 'purr/doggo', 'cat(cats)/dog(dogs)', 'pupper/cat(cats)'],
            "['dog', 'dog']": ['doggo/doggo']})

    def test_dedup_ship_fandom_bug(self):
        shiplist = {"cat(cats)/dog(dogs)": ['kitte/doge', 'purr/doggo'], 'doggo/doggo': [], 'pupper/kitte': []}
        charlist = {'cat': ['kitten', 'kot', 'ket', 'purr', 'kotato', 'kitte'], 'dog': ['pupper', 'doggo', 'doge']}
        dedup_ships = utils.dedup_ship_fandom(shiplist, charlist)
        assert (dedup_ships == {
            "['cat', 'dog']": ['kitte/doge', 'purr/doggo', 'cat(cats)/dog(dogs)', 'pupper/kitte'],
            "['dog', 'dog']": ['doggo/doggo']})

    def test_process_zeus(self):
        fandom_name = 'Blood of Zeus (Cartoon)'
        f = open("resources/" + fandom_name + "/raw/works.json")
        d = json.load(f)
        f.close()
        ext.process_works_file(d, fandom_name)
        # raw_count = self.count_character_raw("Seraphim", fandom_name)
        # processed_count = self.count_character_processed("Seraphim", fandom_name)
        # assert(raw_count == processed_count)
        # raw_count = self.count_character_raw("Apollo", fandom_name)
        # processed_count = self.count_character_processed("Apollo", fandom_name)
        # assert(raw_count == processed_count)
        # raw_count = self.count_character_raw("Hera", fandom_name)
        # processed_count = self.count_character_processed("Hera", fandom_name)
        # assert(raw_count == processed_count)
        # TODO: Deal with edge cases here resulting in +-1
        raw_count = self.count_character_raw("Hermes", fandom_name)
        processed_count = self.count_character_processed("Hermes", fandom_name)
        assert (raw_count == processed_count)
        raw_count = self.count_character_raw("Aphrodite", fandom_name)
        processed_count = self.count_character_processed("Aphrodite", fandom_name)
        assert (raw_count == processed_count)
        # raw_count = self.count_character_raw("Dionysus", fandom_name)
        # processed_count = self.count_character_processed("Dionysus", fandom_name)
        # assert(raw_count == processed_count)

    def test_dedup_zeus_tags(self):
        fandom_name = 'Blood of Zeus (Cartoon)'
        f = open("resources/" + fandom_name + "/raw/tags.json")
        d = json.load(f)
        print(len(d))
        f.close()
        dr = utils.dedup_dict(d)
        print(len(dr))


    def count_character_raw(self, name, fandom_name):
        with open("resources/" + fandom_name + "/raw/works.json") as works:
            d = json.load(works)
            counter = 0
            for work in d.values():
                if name in str(work['characters']) or name in str(work['relationships']):
                    counter += 1
            print(counter)
            return counter

    def count_character_processed(self, name, fandom_name):
        with open("resources/" + fandom_name + "/processed/works.json") as works:
            d = json.load(works)
            counter = 0
            for work in d.values():
                occurrences = work["characters"].count(name)
                counter += occurrences
            return counter
