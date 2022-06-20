from src.database_tree import DatabaseTree
from anytree import Node, RenderTree
import unittest
import json
from src.params.folder_params import *
from anytree.exporter import DotExporter


class database_tree_test(unittest.TestCase):

    def test(self):
        fandom_name = 'Blood of Zeus (Cartoon)'
        with open(ROOT_DIR + FILES_ROOT + fandom_name + RAW_CHARACTERS) as f_t:
            d = json.load(f_t)
            tree = DatabaseTree(d)
            print(len(tree.main_tags))
            print(len(d))
            for root in tree.main_tags:
                for pre, _, node in RenderTree(root):
                    print("%s%s" % (pre, node.name))
            # for root in tree.main_tags:
            #     DotExporter(root).to_picture(root.name + ".png")

    def test_dup(self):
        duplicated = {"cat": ["kitten", "kot", "ket", "purr", "kitte"],
                      "dog": ["pupper", "doggo", "doge"],
                      "kitte": ["kot", "kotato"],
                      "kotato": ["catte"]}
        tree = DatabaseTree(duplicated)
        print(len(tree.main_tags))
        print(len(duplicated))
        for root in tree.main_tags:
            for pre, _, node in RenderTree(root):
                print("%s%s" % (pre, node.name))