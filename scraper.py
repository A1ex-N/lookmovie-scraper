import logging
import sys
from datetime import datetime

import httpx
from selectolax.parser import HTMLParser, Node

from database import Database
from search_result import SearchResult
from search_types import SearchType


class Scraper:
    current_page: int = 0
    base_search_url: str = (
        "https://www.lookmovie2.to/{search_type}/search/page/{page}?q="
    )
    session: httpx.Client
    start_page: int = 1
    end_page: int = 0  # 2564
    start_time = datetime
    processed_pages: int = 0
    movie_list_node: Node
    search_type: SearchType
    results: list[tuple[SearchResult]] = []
    database: Database

    def __init__(
        self, database_name, search_type: SearchType, start_page=1, end_page=0
    ):
        self.start_page = start_page
        self.end_page = end_page
        self.search_type = search_type
        self.database_name = database_name
        self.session = httpx.Client()
        self.database = Database(database_name)

    def start_scraping(self):
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
        self.current_page = page_num
        current_page_url = self.base_search_url.format(
            search_type=self.search_type.value, page=page_num
        )
        try:
            current_page_content = self.session.get(current_page_url)
            self.get_movie_list_node(current_page_content.content)
            for movie_node in self.movie_list_node.iter():
                self.results.append(
                    SearchResult(movie_node, self.current_page).to_tuple()  # type: ignore
                )
            self.processed_pages += 1
        except Exception as e:
            logging.error("Encountered exception %s", e)
            logging.info(
                "Dumping scraped information to %s and exiting", self.database_name
            )
            self.dump_scrape_status()
            sys.exit(1)

    def dump_scrape_status(self):
        if self.search_type == SearchType.MOVIE:
            self.database.insert_new_movies(self.results)
        else:
            self.database.insert_new_series(self.results)

        self.database.close()

        with open("num_pages_scraped.txt", "w") as f:
            f.write(str(self.current_page))
        logging.info(
            "scraped %d movies from %d pages in %s",
            len(self.results),
            self.processed_pages,
            datetime.now() - self.start_time,  # type: ignore
        )

    def get_movie_list_node(self, html: str | bytes) -> Node:
        tree = HTMLParser(html)
        self.movie_list_node = tree.css_first(".flex-wrap-movielist")
        return self.movie_list_node


def main():
    logging.basicConfig(
        handlers=[logging.FileHandler("scrape.log"), logging.StreamHandler()],
        format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
        level=logging.INFO,
    )

    scraper = Scraper("test.db", SearchType.MOVIE, 1, 3)
    scraper.start_scraping()


if __name__ == "__main__":
    main()
