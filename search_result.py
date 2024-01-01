import dataclasses
from datetime import datetime

from selectolax.parser import Node


@dataclasses.dataclass
class SearchResult:
    """
    A class that represents a title (movie/show)
    """

    slug: str
    title: str
    year: str | None
    rating: str | None
    poster_url: str | None
    page_url: str
    search_page_num: int
    search_query: str

    def __init__(self, node: Node, search_page_num: int, search_query: str):
        self.title = self.get_title(node)
        self.page_url = self.get_page_link(node)
        self.rating = self.get_rating(node)
        self.poster_url = self.get_image_link(node)
        self.year = self.get_year(node)
        self.search_page_num = search_page_num
        self.search_query = search_query
        self.slug = self.page_url.split("/")[-1]
        self.scraped_at = self.utc_str()

    def to_tuple(
        self,
    ) -> tuple[str, str, str | None, str | None, str | None, str | None, int, str, str]:
        """
        Returns self represented as a tuple in order to be used in
        sqlite3's executemany() function

        :return: a tuple of self
        """
        return (
            self.slug,
            self.title,
            self.year,
            self.rating,
            self.poster_url,
            self.page_url,
            self.search_page_num,
            self.scraped_at,
            self.search_query,
        )

    @staticmethod
    def get_title(node: Node) -> str:
        """gets the title for a search result"""
        return node.css_first(".mv-item-infor h6 a").text().strip()

    @staticmethod
    def get_rating(node: Node) -> str | None:
        """gets the rating for a search result"""
        try:
            return node.css_first(".image__placeholder a .rate span").text().strip()
        except AttributeError:
            return None

    @staticmethod
    def get_year(node: Node) -> str | None:
        """gets the year for a search result"""
        try:
            return node.css_first(".image__placeholder a .year").text().strip()
        except AttributeError:
            return None

    @staticmethod
    def get_image_link(node: Node) -> str | None:
        """gets the image link for a search result"""
        try:
            return node.css_first(".image__placeholder a img").attributes["data-src"]
        except AttributeError:
            return None

    @staticmethod
    def get_page_link(node: Node) -> str:
        """gets the page link for a search result"""
        # pretty sure this can never be None
        return node.css_first(".hvr-inner a").attributes["href"]

    @staticmethod
    def utc_str():
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
