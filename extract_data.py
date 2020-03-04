from fandom_scraper import Fandom
import json
import pprint
import database_utils as utils
from pathlib import Path
from analysis_tools import FandomAnalysisTools


# 1. Scrape all titles and metadata on a page
# 2. Re-run another scrape to build character database
# 3. Re-run another scrape to build ships database
# 4. Re-run another scrape to build tags database



def extract_works_metadata(fandom, p):
    dict = fandom.get_full_works_metadata()
    dict = utils.ships_to_chars(dict)
    print(dict)
    with open((p / 'works.json'), 'w') as f:
        json.dump(dict, f)

def make_fandom_vars(fandom_name):
    fnd = Fandom(fandom_name)
    p = Path('./fandom_extracted_data/' + fandom_name)
    p.mkdir(exist_ok=True)
    fan = FandomAnalysisTools(fandom_name)
    fan.prepare_analytics_folders()
    return fnd, fan, p

def process_data_files(fandom_name):
    print("Processing character names to minimise duplication.")
    with open("fandom_extracted_data/" + fandom_name + "/characters.json") as f_c:
        d = json.load(f_c)
        d = utils.dedup_dict(d)
        d = utils.dedup_char_fandom(d)
        with open("fandom_extracted_data/" + fandom_name + "/characters.json", 'w') as w_c:
            json.dump(d, w_c)
    print("Processing tag names to minimise duplication.")
    with open("fandom_extracted_data/" + fandom_name + "/tags.json") as f_t:
        d = json.load(f_t)
        d = utils.dedup_dict(d)
        with open("fandom_extracted_data/" + fandom_name + "/tags.json", 'w') as w_t:
            json.dump(d, w_t)
    print("Processing relationships to minimise duplication.")
    with open("fandom_extracted_data/" + fandom_name + "/characters.json") as f_c:
        char_dict = json.load(f_c)
        with open("fandom_extracted_data/" + fandom_name + "/ships.json") as f_s:
            d = json.load(f_s)
            d = utils.dedup_dict(d)
            print(d)
            d = utils.dedup_ship_fandom(d, char_dict)
            with open("fandom_extracted_data/" + fandom_name + "/ships.json", 'w') as w_s:
                json.dump(d, w_s)

def process_works_file(d, fandom_name):
    with open("fandom_extracted_data/" + fandom_name + "/characters.json") as f_c:
        with open("fandom_extracted_data/" + fandom_name + "/tags.json") as f_t:
            with open("fandom_extracted_data/" + fandom_name + "/ships.json") as f_s:
                char_dict = json.load(f_c)
                tag_dict = json.load(f_t)
                ship_dict = json.load(f_s)
                utils.process_dict(d, char_dict, tag_dict, ship_dict)
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint(d)
                with open("fandom_extracted_data/" + fandom_name + "/works.json", 'w') as w_w:
                    json.dump(d, w_w)



def get_chars_ships_tags_variants(fan, fnd, fandom_name):
    with open("fandom_extracted_data/" + fandom_name + "/works.json") as f:
        d = json.load(f)
        tags_raw = fan.get_top_tags(d)
        chars_raw = fan.get_top_characters(d)
        ships_raw = fan.get_top_ships(d)
        chars = fnd.get_all_fandom_characters(chars_raw)
        with open("fandom_extracted_data/" + fandom_name + "/characters.json", 'w') as f_c:
            json.dump(chars, f_c)
        tags = fnd.get_all_fandom_tags(tags_raw)
        with open("fandom_extracted_data/" + fandom_name + "/tags.json", 'w') as f_t:
            json.dump(tags, f_t)
        ships = fnd.get_all_fandom_ships(ships_raw)
        print(ships)
        with open("fandom_extracted_data/" + fandom_name + "/ships.json", 'w') as f_s:
            json.dump(ships, f_s)

def main():
    fandom_name = 'What We Do in the Shadows (2014)'
    fnd, fan, p = make_fandom_vars(fandom_name)
    # extract_works_metadata(fnd, p)
    # get_chars_ships_tags_variants(fan, fnd, fandom_name)
    process_data_files(fandom_name)
    with open("fandom_extracted_data/" + fandom_name + "/works.json") as f:
        d = json.load(f)
        process_works_file(d, fandom_name)
        fan.prepare_analytics_folders()
        fan.do_analysis(d)

if __name__== "__main__":
    main()