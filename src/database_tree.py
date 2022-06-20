from anytree import Node, RenderTree
from typing import List
import json

from src.params.folder_params import *

class DatabaseTree:

    # def __main__(self):
    #     fandom_name = 'Blood of Zeus (Cartoon)'
    #     with open(ROOT_DIR + FILES_ROOT + fandom_name + RAW_TAGS) as f_t:
    #         d = json.load(f_t)
    #         self.init_database(d)

    main_tags: List[Node] = []

    def __init__(self, tag_dict: dict):
        parentless: List[str] = self.find_parentless_tags(tag_dict)
        root_list: List[Node] = [Node(x, children=self.make_nodes(tag_dict[x])) for x in parentless]
        self.distribute_other_tags(tag_dict, parentless, root_list)
        self.main_tags = root_list

    @staticmethod
    def make_nodes(list_nodes: List[str]):
        return [Node(x) for x in list_nodes]

    def find_parentless_tags(self, tag_dict: dict) -> List[str]:
        parentless: list = []
        for key in tag_dict.keys():
            if self.is_parentless(key, tag_dict):
                parentless.append(key)
        return parentless

    def is_parentless(self, tag, tag_dict):
        for parent in tag_dict.keys():
            if tag in tag_dict[parent]:
                return False
        return True

    def distribute_other_tags(self, tag_dict: dict, parentless: List[str], root_list: List[Node]):
        for key in tag_dict.keys():
            if key not in parentless:
                for root in root_list:
                    self.dfs_insert(key, tag_dict[key], root)

    def dfs_insert(self, key: str, value: List[str], root:Node):
        for child in root.children:
            if child.name == key:
                child.children = self.make_nodes(value)
                return
            self.dfs_insert(key, value, child)
        return



