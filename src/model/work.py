import datetime
from typing import List


class Work:
    title: str
    chapters: int
    hits: int
    kudos: int
    words: int
    date_updated: datetime.datetime
    tags: List[str]
    characters: List[str]
    rating: str
    authors: List[str]
    relationships: List
    categories: List[str]
    summary: str
