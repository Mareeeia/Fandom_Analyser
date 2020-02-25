from fandom_scraper import Fandom
import json
from pathlib import Path
from analysis_tools import FandomAnalysisTools


# 1. Scrape all titles and metadata on a page
# 2. Re-run another scrape to build character database
# 3. Re-run another scrape to build ships database
# 4. Re-run another scrape to build tags database



def extract_works_metadata(fandom):

    dict = fandom.get_full_works_metadata()
    with open((p / 'works.json'), 'w') as f:
        json.dump(dict, f)

def make_fandom_vars(fandom_name):
    fnd = Fandom(fandom_name)
    p = Path('./fandom_extracted_data/' + fandom_name)
    p.mkdir(exist_ok=True)
    fan = FandomAnalysisTools(fandom_name)
    fan.prepare_analytics_folders()
    return fnd, fan

def process_data_files():
    print("Processing names to minimise duplication.")

def extract_tag_varians():
    return tags


def extract_character_varians():
    return characters

def extract_ship_variants():
    return ships

def main():
    fandom_name = 'Legacy of Kain'
    fnd, fan = make_fandom_vars(fandom_name)
    with open("fandom_extracted_data/" + fandom_name + "/works.json") as f:
        d = json.load(f)
        chars_raw = fan.get_top_characters(d)
        chars = fnd.get_all_fandom_characters(chars_raw)
        with open("fandom_extracted_data/" + fandom_name + "/characters.json", 'w') as f:
            json.dump(chars, f)

if __name__== "__main__":
    main()