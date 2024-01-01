import logging
import sys
from datetime import datetime
from typing import Optional

import httpx
from selectolax.parser import HTMLParser, Node

from database import Database
from search_result import SearchResult
from search_types import SearchType


class Scraper:
    """
    Class used for scraping search pages from https://lookmovie2.to
    """

    base_search_url: str = (
        "https://www.lookmovie2.to/{search_type}/search/page/{page}?q={search_query}"
    )
    session: httpx.Client
    start_page: int = 1
    end_page: int = 0  # 2564
    start_time = datetime
    processed_pages: int = 0
    search_query: str
    search_type: SearchType
    results: list[tuple[SearchResult]] = []
    database: Database

    def __init__(
        self,
        database_name,
        search_type: SearchType,
        search_query: str = "",
        start_page=1,
        end_page=0,
    ):
        self.start_page = start_page
        self.end_page = end_page
        self.search_type = search_type
        self.database_name = database_name
        self.session = httpx.Client()
        self.search_query = search_query
        self.database = Database(database_name)

    def start_scraping(self):
        """
        loops from self.start_page to self.end_page + 1,
        running self.get_episode(page_num) on each iteration
        """
        self.start_time = datetime.now()
        logging.info(
            "starting scrape from page %d to %d",
            self.start_page,
            self.end_page,
        )
        for page_num in range(self.start_page, self.end_page + 1):
            self.get_episode(page_num)
        self.dump_scrape_status()

    def get_episode(self, page_num: int):
        """
        Gets all the information for each title (movie/show) on page_num
        and appends them to self.results.

        If the status code of the page request is not 200 the current
        scraped titles will be dumped to the database and the program
        will exit with code 1

        :param page_num: the page to scrape
        """
        current_page_url = self.base_search_url.format(
            search_type=self.search_type.value,
            search_query=self.search_query,
            page=page_num,
        )
        current_page_content = self.session.get(current_page_url)
        if current_page_content.status_code != 200:
            logging.info(
                "Status code for %s was not 200. Dumping scraped titles and exiting.",
                current_page_url,
            )
            self.dump_scrape_status()
            sys.exit(1)

        movie_list_node = self.get_movie_list_node(current_page_content.content)
        if movie_list_node is None:
            logging.error("Cannot get movie list node")
            exit(1)
        for movie_node in movie_list_node.iter():
            self.results.append(
                SearchResult(movie_node, page_num, self.search_query).to_tuple()  # type: ignore
            )
        self.processed_pages += 1

    def dump_scrape_status(self):
        """
        dumps all scraped titles (movies/shows) to the database
        """
        self.database.insert_search_results(self.results, self.search_type)
        self.database.close()

        logging.info(
            "scraped %d %s from %d pages in %s",
            len(self.results),
            self.search_type.value,
            self.processed_pages,
            datetime.now() - self.start_time,  # type: ignore
        )

    @staticmethod
    def get_movie_list_node(html: str | bytes) -> Optional[Node]:
        """
        Gets the movie list Node (HTML element containing each title (movie/show))

        :param html: the html of the page to get the node from
        :return: selectolax.parser.Node
        """
        tree = HTMLParser(html)
        return tree.css_first(".flex-wrap-movielist")


def main():
    """Initialises logging and runs the Scraper"""
    logging.basicConfig(
        handlers=[logging.FileHandler("scrape.log"), logging.StreamHandler()],
        format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
        level=logging.INFO,
    )

    #scraper = Scraper("database/scraped_data.db", SearchType.MOVIE, start_page=1, end_page=124)
    scraper = Scraper("test.db", SearchType.MOVIE, start_page=1, end_page=2)
    scraper.start_scraping()


if __name__ == "__main__":
    main()
