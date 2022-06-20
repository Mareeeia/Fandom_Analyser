import json
import src.database_utils as utils
from src.fandom_scraper import Fandom
from src.params.folder_params import *
import pandas as pd
from pathlib import Path


# 1. Scrape all titles and metadata on a page
# 2. Re-run another scrape to build character database
# 3. Re-run another scrape to build ships database
# 4. Re-run another scrape to build tags database

def extract_and_process(fandom_name: str):
    print(fandom_name)
    fnd, p = make_fandom_vars(fandom_name)
    extract_works_metadata(fnd, p)
    get_tags(fnd, fandom_name)
    get_chars(fnd, fandom_name)
    get_ships(fnd, fandom_name)
    process_data_files(fandom_name)


def extract_works_metadata(fandom, p) -> dict:
    # TODO: put an option to avoid deeep scrape
    works_dict = fandom.get_full_works_metadata()
    works_dict = utils.ships_to_chars(works_dict)
    p = Path(p / 'raw')
    with open((p / 'works.json'), 'w') as f:
        json.dump(works_dict, f)
    return works_dict


def make_fandom_vars(fandom_name):
    fnd = Fandom(fandom_name)
    p = Path(ROOT_DIR + '/fandom_extracted_data/' + fandom_name)
    p.mkdir(exist_ok=True)
    Path(p / 'raw').mkdir(exist_ok=True)
    Path(p / 'processed').mkdir(exist_ok=True)
    return fnd, p


def process_data_files(fandom_name):
    print("Processing character names to minimise duplication.")
    with open(ROOT_DIR + FILES_ROOT + fandom_name + RAW_CHARACTERS) as f_c:
        d = json.load(f_c)
        d = utils.dedup_dict(d)
        d = utils.dedup_char_fandom(d)
        with open(ROOT_DIR + FILES_ROOT + fandom_name + PROCESSED_CHARACTERS, 'w') as w_c:
            json.dump(d, w_c)
    print("Processing tag names to minimise duplication.")
    with open(ROOT_DIR + FILES_ROOT + fandom_name + RAW_TAGS) as f_t:
        d = json.load(f_t)
        d = utils.dedup_dict(d)
        with open(ROOT_DIR + FILES_ROOT + fandom_name + PROCESSED_TAGS, 'w') as w_t:
            json.dump(d, w_t)
    print("Processing relationships to minimise duplication.")
    with open(ROOT_DIR + FILES_ROOT + fandom_name + RAW_CHARACTERS) as f_c:
        char_dict = json.load(f_c)
        with open(ROOT_DIR + FILES_ROOT + fandom_name + RAW_SHIPS) as f_s:
            d = json.load(f_s)
            d = utils.dedup_dict(d)
            d = utils.dedup_ship_fandom(d, char_dict)
            with open(ROOT_DIR + FILES_ROOT + fandom_name + PROCESSED_SHIPS, 'w') as w_s:
                json.dump(d, w_s)


def process_works_file(d, fandom_name):
    with open(ROOT_DIR + FILES_ROOT + fandom_name + PROCESSED_CHARACTERS) as f_c:
        with open(ROOT_DIR + FILES_ROOT + fandom_name + PROCESSED_TAGS) as f_t:
            with open(ROOT_DIR + FILES_ROOT + fandom_name + PROCESSED_SHIPS) as f_s:
                char_dict = json.load(f_c)
                tag_dict = json.load(f_t)
                ship_dict = json.load(f_s)
                utils.process_dict(d, char_dict, tag_dict, ship_dict)
                with open(ROOT_DIR + FILES_ROOT + fandom_name + PROCESSED_WORKS, 'w') as w_w:
                    json.dump(d, w_w)


def get_chars(fnd, fandom_name, count=0):
    with open(ROOT_DIR + FILES_ROOT + fandom_name + RAW_WORKS) as f:
        d = json.load(f)
        chars_raw = get_top_characters(d, count)
        chars = fnd.get_all_fandom_characters(chars_raw)
        with open(ROOT_DIR + FILES_ROOT + fandom_name + RAW_CHARACTERS, 'w') as f_c:
            json.dump(chars, f_c)


def get_tags(fnd, fandom_name, count=0):
    with open(ROOT_DIR + FILES_ROOT + fandom_name + RAW_WORKS) as f:
        d = json.load(f)
        tags_raw = get_top_tags(d, count)
        tags = fnd.get_all_fandom_tags(tags_raw)
        with open(ROOT_DIR + FILES_ROOT + fandom_name + RAW_TAGS, 'w') as f_t:
            json.dump(tags, f_t)


def get_ships(fnd, fandom_name, count=0):
    with open(ROOT_DIR + FILES_ROOT + fandom_name + RAW_WORKS) as f:
        d = json.load(f)
        ships_raw = get_top_ships(d, count)
        ships = fnd.get_all_fandom_ships(ships_raw)
        with open(ROOT_DIR + FILES_ROOT + fandom_name + RAW_SHIPS, 'w') as f_t:
            json.dump(ships, f_t)


def get_top_characters(d, count=0):
    df = pd.DataFrame.from_dict(d, orient='index')
    df = df['characters'].explode().value_counts().rename_axis('Characters').reset_index(name='Fanfic Counts')
    is_large = df['Fanfic Counts'] > 0
    if count > 0:
        df = df.head(count)
    else:
        df = df[is_large]
    return df['Characters'].values


def get_top_tags(d, count=0):
    df = pd.DataFrame.from_dict(d, orient='index')
    df = df['tags'].explode().value_counts().rename_axis('Tags').reset_index(name='Fanfic Counts')
    is_large = df['Fanfic Counts'] > 0
    if count > 0:
        df = df.head(count)
    else:
        df = df[is_large]
    return df['Tags'].values


def get_top_ships(d, count=0):
    df = pd.DataFrame.from_dict(d, orient='index')
    df = df['relationships'].explode().value_counts().rename_axis('Ships').reset_index(name='Fanfic Counts')
    is_large = df['Fanfic Counts'] > 0
    if count > 0:
        df = df.head(count)
    else:
        df = df[is_large]
    return df['Ships'].values


if __name__ == "__main__":
    main()
