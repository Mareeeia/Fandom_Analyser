from fandom_scraper import Fandom
import json
from pathlib import Path
from analysis_tools import FandomAnalysisTools


# 1. Scrape all titles and metadata on a page
# 2. Re-run another scrape to build character database
# 3. Re-run another scrape to build ships database
# 4. Re-run another scrape to build tags database



def extract_works_metadata(fandom, p):

    dict = fandom.get_full_works_metadata()
    with open((p / 'works.json'), 'w') as f:
        json.dump(dict, f)

def make_fandom_vars(fandom_name):
    fnd = Fandom(fandom_name)
    p = Path('./fandom_extracted_data/' + fandom_name)
    p.mkdir(exist_ok=True)
    fan = FandomAnalysisTools(fandom_name)
    fan.prepare_analytics_folders()
    return fnd, fan, p

def process_data_files():
    print("Processing names to minimise duplication.")

def extract_tag_varians():
    return tags


def extract_character_varians():
    return characters

def extract_ship_variants():
    return ships

def main():
    fandom_name = '龍が如く%20%7C%20Ryuu%20ga%20Gotoku%20%7C%20Yakuza%20(Video%20Games)'
    fnd, fan, p = make_fandom_vars(fandom_name)
    # extract_works_metadata(fnd, p)
    with open("fandom_extracted_data/" + fandom_name + "/works.json") as f:
        d = json.load(f)
        tags_raw = fan.get_top_tags(d)
        chars_raw = fan.get_top_characters(d)
        ships_raw = fan.get_top_ships(d)
        fan.prepare_analytics_folders()
        fan.do_analysis(d)
        # print(ships_raw)
        # print(chars_raw)
        # print(tags_raw)
        chars = fnd.get_all_fandom_characters(chars_raw)
        with open("fandom_extracted_data/" + fandom_name + "/characters.json", 'w') as f_c:
            json.dump(chars, f_c)
        tags = fnd.get_all_fandom_tags(tags_raw)
        with open("fandom_extracted_data/" + fandom_name + "/tags.json", 'w') as f_t:
            json.dump(tags, f_t)
        ships = fnd.get_all_fandom_ships(ships_raw)
        with open("fandom_extracted_data/" + fandom_name + "/ships.json", 'w') as f_s:
            json.dump(ships, f_s)

if __name__== "__main__":
    main()