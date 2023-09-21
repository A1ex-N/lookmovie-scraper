import dataclasses

from selectolax.parser import Node


@dataclasses.dataclass
class SearchResult:
    """
    A class that represents a title (movie/show)
    """

    title: str
    year: str | None
    rating: str | None
    poster_url: str | None
    page_url: str | None
    search_page_num: int

    def __init__(self, node: Node, search_page_num: int):
        self.title = self.get_title(node)
        self.page_url = self.get_page_link(node)
        self.rating = self.get_rating(node)
        self.poster_url = self.get_image_link(node)
        self.year = self.get_year(node)
        self.search_page_num = search_page_num

    def to_tuple(
        self,
    ) -> tuple[str, str | None, str | None, str | None, str | None, int]:
        """
        Returns self represented as a tuple in order to be used in
        sqlite3's executemany() function

        :return: a tuple of self
        """
        return (
            self.title,
            self.year,
            self.rating,
            self.poster_url,
            self.page_url,
            self.search_page_num,
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
    def get_page_link(node: Node) -> str | None:
        """gets the page link for a search result"""
        try:
            return node.css_first(".hvr-inner a").attributes["href"]
        except AttributeError:
            return None
