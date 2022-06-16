from src.fandom_scraper import Fandom
import json
import logging
import src.database_utils as utils
from src.params.folder_params import *
from pathlib import Path
from src.analysis_tools import FandomAnalysisTools


# 1. Scrape all titles and metadata on a page
# 2. Re-run another scrape to build character database
# 3. Re-run another scrape to build ships database
# 4. Re-run another scrape to build tags database

logger_extract = logging.getLogger("extract")


def extract_works_metadata(fandom, p):
    dict = fandom.get_full_works_metadata()
    dict = utils.ships_to_chars(dict)
    logger_extract.debug(dict)
    p = Path(p / 'raw')
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
    logger_extract.info("Processing character names to minimise duplication.")
    with open(FILES_ROOT + fandom_name + RAW_CHARACTERS) as f_c:
        d = json.load(f_c)
        d = utils.dedup_dict(d)
        d = utils.dedup_char_fandom(d)
        logger_extract.debug(d)
        with open(FILES_ROOT + fandom_name + PROCESSED_CHARACTERS, 'w') as w_c:
            json.dump(d, w_c)
    logger_extract.info("Processing tag names to minimise duplication.")
    with open(FILES_ROOT + fandom_name + RAW_TAGS) as f_t:
        d = json.load(f_t)
        d = utils.dedup_dict(d)
        logger_extract.debug(d)
        with open(FILES_ROOT + fandom_name + PROCESSED_TAGS, 'w') as w_t:
            json.dump(d, w_t)
    logger_extract.info("Processing relationships to minimise duplication.")
    with open(FILES_ROOT + fandom_name + RAW_CHARACTERS) as f_c:
        char_dict = json.load(f_c)
        with open(FILES_ROOT + fandom_name + RAW_SHIPS) as f_s:
            d = json.load(f_s)
            d = utils.dedup_dict(d)
            logger_extract.debug(d)
            d = utils.dedup_ship_fandom(d, char_dict)
            with open(FILES_ROOT + fandom_name + PROCESSED_SHIPS, 'w') as w_s:
                json.dump(d, w_s)


def process_works_file(d, fandom_name, prefix="", file=FILES_ROOT):
    with open(prefix + file + fandom_name + PROCESSED_CHARACTERS) as f_c:
        with open(prefix + file + fandom_name + PROCESSED_TAGS) as f_t:
            with open(prefix + file + fandom_name + PROCESSED_SHIPS) as f_s:
                char_dict = json.load(f_c)
                tag_dict = json.load(f_t)
                ship_dict = json.load(f_s)
                utils.process_dict(d, char_dict, tag_dict, ship_dict)
                logger_extract.debug(d)
                with open(prefix + file + fandom_name + PROCESSED_WORKS, 'w') as w_w:
                    json.dump(d, w_w)


def get_chars(fan, fnd, fandom_name):
    with open(FILES_ROOT + fandom_name + RAW_WORKS) as f:
        d = json.load(f)
        chars_raw = fan.get_top_characters(d)
        chars = fnd.get_all_fandom_characters(chars_raw)
        with open(FILES_ROOT + fandom_name + RAW_CHARACTERS, 'w') as f_c:
            json.dump(chars, f_c)


def get_tags(fan, fnd, fandom_name):
    with open(FILES_ROOT + fandom_name + RAW_WORKS) as f:
        d = json.load(f)
        tags_raw = fan.get_top_tags(d)
        tags = fnd.get_all_fandom_tags(tags_raw)
        with open(FILES_ROOT + fandom_name + RAW_TAGS, 'w') as f_t:
            json.dump(tags, f_t)


def get_ships(fan, fnd, fandom_name):
    with open(FILES_ROOT + fandom_name + RAW_WORKS) as f:
        d = json.load(f)
        ships_raw = fan.get_top_ships(d)
        ships = fnd.get_all_fandom_ships(ships_raw)
        with open(FILES_ROOT + fandom_name + RAW_SHIPS, 'w') as f_t:
            json.dump(ships, f_t)


if __name__ == "__main__":
    main()
