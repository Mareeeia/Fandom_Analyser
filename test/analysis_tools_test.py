import json
import unittest
import src.database_utils as utils
import src.extract_data as ext
from src.analysis_tools import FandomAnalysisTools


class analysis_tools_test(unittest.TestCase):
    fandom_name = 'Blood of Zeus (Cartoon)'
    fan = FandomAnalysisTools(fandom_name)

    def test_ratings_count(self):
        with open("../src/fandom_extracted_data/" + self.fandom_name + "/processed/works.json") as f_c:
            d = json.load(f_c)
            self.fan.plot_new_works_count_by_month_ratings(d)
        assert(True)

    def test_count_category(self):
        with open("../src/fandom_extracted_data/" + self.fandom_name + "/processed/works.json") as f_c:
            d = json.load(f_c)
            self.fan.plot_works_count_by_category(d)
        assert(True)