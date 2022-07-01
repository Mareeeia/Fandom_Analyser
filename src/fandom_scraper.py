import datetime
import json
from datetime import date
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
import re
import math
import sys
from stem import Signal
from stem.control import Controller
import logging

from src.params.folder_params import *


class Fandom:

    def __init__(self, fandom_name):
        self.fandom = fandom_name
        self.soup_works = self.request("https://archiveofourown.org/tags/%s/works?page=1" % (fandom_name))
        print("https://archiveofourown.org/tags/%s/works?page=1" % (fandom_name))
        self.loaded_page = 1
        self.soup_profile = self.request("https://archiveofourown.org/tags/%s/profile" % fandom_name)
        with open(ROOT_DIR + COMBINED_TAGS) as tags_file:
            self.tags_dict = json.load(tags_file)

    @property
    def works(self):
        header = str(self.soup_works.find("h2", {'class': 'heading'}))
        match = re.search('(\\d+) Works in', header)
        return int(match.group(1))

    @property
    def npages(self):
        return (self.works - 1) // 20 + 1

    def get_work_list_page(self, page=1):
        """Returns the first 20 works by the author, unless the page is specified"""
        if self.loaded_page != page:
            self.soup_works = self.request("https://archiveofourown.org/tags/%s/works?page=%i" % (self.fandom, page))
            self.loaded_page = page

        ol = self.soup_works.find("ol", {'class': 'work index group'})
        works = {}
        for work in ol.find_all("li", {'role': 'article'}):
            works[int(self.str_format(work['id'].split("_")[-1]))] = work.a.string.strip()
        return works

    def get_works_metadata_page(self, page=1):
        """Returns the first 20 works by the author, unless the page is specified"""
        if self.loaded_page != page:
            self.soup_works = self.request("https://archiveofourown.org/tags/%s/works?page=%i" % (self.fandom, page))
            self.loaded_page = page
        beautiful_soup = self.soup_works.find("ol", {'class': 'work index group'})
        works = {}
        try:
            for work in beautiful_soup.find_all("li", {'role': 'article'}):
                id = self.str_format(work['id'].split("_")[-1])
                works[int(id)] = self.get_work_metadata(work, id)
        except:
            print(len(self.soup_works))
            print(str(self.soup_works))
        return works

    # def get_full_works_titles(self):
    #     pagecount = (self.works - 1) // 20
    #     works_list = {}
    #     for i in range(1, pagecount):
    #         print("Currently fetching titles page: ", i)
    #         titles = self.get_work_list_page(i)
    #         works_list.update(titles)
    #         if i % 10 == 0:
    #             print("Sleeping 120 sec to avoid trouble")
    #             time.sleep(120)
    #     return works_list

    def get_full_works_metadata(self):
        pagecount = math.ceil(self.works / 20.0)
        print("Fandom contains " + str(self.works) + " works in " + str(pagecount) + " pages.")
        works_dict = {}
        for i in range(1, pagecount + 1):
            print("Currently fetching titles page: " + str(i))
            metadatas = self.get_works_metadata_page(i)
            works_dict.update(metadatas)
        return works_dict

    def get_work_metadata(self, soup, id):
        work_properties = {
            "title": self.get_title(soup, id),
            "chapters": self.get_chapters(soup, id),
            "hits": self.get_hits(soup, id),
            "kudos": self.get_kudos(soup, id),
            "words": self.get_words(soup, id),
            # "date_published": self.get_date_published(soup, id),
            "date_updated": self.get_date_updated(soup, id),
            "tags": self.get_tags(soup, id),
            "characters": self.get_characters(soup, id),
            "rating": self.get_ratings(soup, id),
            "authors": self.get_authors(soup, id),
            "relationships": self.get_relationships(soup, id),
            "categories": self.get_categories(soup, id),
            "summary": self.get_summary(soup, id)
        }
        return work_properties

    # def get_full_works(self, works_list):
    #     sleepcount = 0
    #     works_full = {}
    #     for id in works_list:
    #         sleepcount = sleepcount + 1
    #         print("Fetching work: ", works_list[id])
    #         wrk = Work(int(id))
    #         works_full[works_list[id]] = wrk.work_properties
    #         if sleepcount % 40 == 0:
    #             print("Sleeping 300 sec to avoid trouble")
    #             time.sleep(360)
    #     return works_full

    # Get
    def get_title(self, soup, id):
        title = soup.find("h4", {'class': 'heading'})
        try:
            title = title.a.string
        except:
            print('Warning: Work id ' + id + ' has no displayed title.')
            title = "Untitled"
        return str(title).strip()

    # Get
    def get_chapters(self, soup, id):
        try:
            chapters = str(soup.find("dd", {'class': 'chapters'})).split("/")[0].split(">")[1]
            return int(self.str_format(chapters))
        except:
            return 1

    # Get
    def get_hits(self, soup, id):
        try:
            hits = str(soup.find("dd", {'class': 'hits'}))
            return int(self.str_format(re.findall(r'\d+', hits)[0]))
        except:
            print('Warning: Work id ' + id + ' has no displayed hits.')
            return 1

    # Get
    def get_kudos(self, soup: BeautifulSoup, id):
        # kudos = str(soup.find("dd", {'class': 'kudos'}))
        try:
            kudos = soup.find('dd', class_='kudos').contents[0].contents[0]
            return kudos
        except:
            return 0
        # if len(re.findall(r'\d+', kudos)) is not 0:
        #     return int(self.str_format(re.findall(r'\d+', kudos)[1]))  # get second digit

    # Get
    def get_words(self, soup, id):
        try:
            words = soup.find("dd", {'class': 'words'})
            return int(self.str_format(words.string))
        except:
            print('Warning: Work id ' + id + ' has no displayed word count')
            return 0

    # Get
    def get_date_published(self, soup, id):
        dp = str(soup.find("dd", {'class': 'published'}))
        dp = ''.join(re.findall(r'-*\d+', dp))
        return str(date(*list(map(int, dp.split("-")))))

    # Get
    def get_date_updated(self, soup, id):
        du = str(soup.find("p", {'class': 'datetime'}).text)
        d = datetime.strptime(du, '%d %b %Y')
        return d.date().isoformat()

    # Get
    def get_tags(self, soup, id):
        html = soup.findAll("li", {'class': 'freeforms'})
        if html is not None:
            tags = []
            for tag in html:
                tags.append(tag.a.string)
            return tags
        else:
            return None

    # Get
    def get_characters(self, soup, id):
        html = soup.findAll("li", {'class': 'characters'})
        characters = []
        if html is not None:
            for character in html:
                characters.append(character.a.string)
            return characters
        else:
            return None

    # Get
    def get_warnings(self, soup, id):
        html = soup.findAll("li", {'class': 'warnings'})
        characters = []
        if html is not None:
            for character in html:
                characters.append(character.a.string)
            return characters
        else:
            return None

    # Get
    def get_relationships(self, soup, id):
        html = soup.findAll("li", {'class': 'relationships'})
        relationships = []
        try:
            for relationship in html:
                relationships.append(relationship.a.string)
        except:
            relationships = []
        return relationships

    # Get
    def get_fandoms(self, soup):
        html = soup.find("dd", {'class': 'fandom tags'})
        fandoms = []
        for fandom in html.find_all("li"):
            fandoms.append(fandom.a.string)
        return fandoms

    # Get
    def get_warnings(self, soup, id):
        html = soup.find("dd", {'class': 'warning tags'})
        warnings = []
        for warning in html.find_all("li"):
            warnings.append(warning.a.string)
        return warnings

    # Get
    def get_ratings(self, soup, id):
        html = soup.find("span", {'class': re.compile(r'rating.*')})
        rating = html.span.string
        return rating

    # Get
    def get_authors(self, soup, id):
        authors = soup.find_all("a", {'rel': 'author'})
        author_list = []
        for author in authors:
            author_list.append(author.string.strip())

        return author_list

    # Get
    def get_categories(self, soup, id):
        html = soup.find("span", {'class': re.compile(r'category.*')})
        return html.span.string.split(', ')

    # Get
    def get_summary(self, soup, id):
        html = soup.find("blockquote", {'class': 'userstuff summary'})
        if html != None:
            return str(html.p.string)
        else:
            return ''

    # Get
    def get_bookmarks(self, soup, id):
        bookmarks = str(soup.find("dd", {'class': 'bookmarks'}))
        return int(self.str_format(re.findall(r'\d+', bookmarks)[0]))

    # Get
    def get_comments(self, soup, id):
        comments = str(soup.find("dd", {'class': 'comments'}))
        return int(self.str_format(re.findall(r'\d+', comments)[0]))

    # Get
    def get_language(self, soup, id):
        language = str(soup.find("dd", {'class': 'language'})).strip()
        return language

    def get_all_fandom_dicts(self):
        self.get_all_fandom_characters()
        self.get_all_fandom_ships()
        self.get_all_fandom_tags()

    def get_all_fandom_characters(self, chars=[]):
        print("Scraping characters from fandom page. We do this to ensure all versions of a character name count as the same character.")
        characters = {}
        if len(chars) == 0:
            chars = self.fandom_page.find("div", {"class": "characters listbox group"})
        for i, char in enumerate(chars):
            characters[char] = self.get_character_variants(char)
            self.progress(i, len(chars))

        print("Finished getting %i characters." % (len(characters)))
        return characters

    def get_character_variants(self, char):
        char_page = self.request("https://archiveofourown.org/tags/%s" % (char))
        variants_div = char_page.find("div", {"class": "synonym listbox group"})
        variants = []
        if variants_div:
            variants_li = variants_div.ul
            for var in variants_li:
                variants.append(self.clean_char_name(var.string))
        return variants

    def clean_char_name(self, char):
        return char.strip()

    def get_all_fandom_ships(self, ships=[]):
        print(
            "Scraping ships from fandom page. We do this to ensure all versions of a ship name count as the same ship.")
        relationships = {}
        if len(ships) == 0:
            ships = self.fandom_page.find("div", {"class": "relationships listbox group"})
        for i, ship in enumerate(ships):
            relationships[ship] = self.get_ship_variants(ship)
            self.progress(i, len(ships))
        print("Finished getting %i ships." % (len(relationships)))
        return relationships

    def get_ship_variants(self, ship):
        ship_page = self.request("https://archiveofourown.org/tags/%s" % (ship))
        variants_div = ship_page.find("div", {"class": "synonym listbox group"})
        variants = []
        if variants_div:
            variants_li = variants_div.ul
            for var in variants_li:
                variants.append(self.clean_ship_name(var.string))
        return variants

    def clean_ship_name(self, ship):
        return ship.strip()

    def clean_tag_name(self, tag):
        return tag.strip()

    def get_all_fandom_tags(self, tags=[]):
        print(
            "Scraping freeform tags from fandom page. We do this to ensure all versions of a tag count as the same tag.")
        tags_dict = {}
        if len(tags) == 0:
            tags = self.fandom_page.find("div", {"class": "freeforms listbox group"})
        for i, tag in enumerate(tags):
            tags_dict[tag] = self.get_tag_variants(tag)
            self.progress(i, len(tags))
        print("Finished getting %i tags." % (len(tags_dict)))
        return tags_dict

    def get_tag_variants(self, tag):
        if tag in self.tags_dict.keys():
            print("Tag %s found in existing files" % tag)
            return self.tags_dict[tag]
        tag_page = self.request("https://archiveofourown.org/tags/%s" % (tag))
        variants_div = tag_page.find("div", {"class": "synonym listbox group"})
        variants = []
        if variants_div:
            variants_li = variants_div.ul
            for var in variants_li:
                variants.append(self.clean_tag_name(var.string))
        return variants

    def progress(self, count, total, status=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '=' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
        sys.stdout.flush()

    @property
    def url(self):
        return "https://archiveofourown.org/tags/%s" % self.fandom

    def request(self, url):
        # for i in range(10):
        #     r = Fandom.request_with_tor('http://httpbin.org/ip')
        #     print(r.text)
        retries = 1
        success = False
        while not success and retries < 6:
            try:
                req = self.request_with_soup(url)
                content = req.content
                soup = BeautifulSoup(content, "html.parser")
                if str(soup) is not "Retry Later" and "Retry" not in str(soup) and len(str(soup)) > 200:
                    success = True
                else:
                    self.wait_to_retry(retries)
                    retries += 1
                return soup
            except Exception as e:
                print(e)
                self.wait_to_retry(retries)
                retries += 1

    @staticmethod
    def wait_to_retry(retries):
        wait = retries * 60
        print('Oops, we sent too many requests to Ao3! Waiting %s secs and re-trying...' % wait)
        sys.stdout.flush()
        time.sleep(wait)


    @staticmethod
    def request_with_tor(url):
        session = requests.session()
        session.proxies = {}
        session.proxies['http'] = 'socks5h://localhost:9150'
        session.proxies['https'] = 'socks5h://localhost:9150'
        headers = requests.utils.default_headers()
        headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'})
        req = session.get(url, headers=headers, timeout=30)
        Fandom.renew_connection()
        return req

    @staticmethod
    def request_with_soup(url):
        return requests.get(url)

    @staticmethod
    def renew_connection():
        with Controller.from_port(port=9152) as controller:
            controller.authenticate(password="password")
            controller.signal(Signal.NEWNYM)

    @staticmethod
    def str_format(string):
        return string.replace(",", "")
