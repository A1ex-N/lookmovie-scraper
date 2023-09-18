import sqlite3
from typing import Coroutine, Any

import httpx

from search_result import SearchResult
from selectolax.parser import HTMLParser, Node
from pprint import pprint
from datetime import datetime
from search_types import SearchType


class Scraper:
    current_page: int = 0
    home_page_url: str = "https://www.lookmovie2.to/"
    base_search_url: str = (
        "https://www.lookmovie2.to/{search_type}/search/page/{page}?q="
    )
    session: httpx.Client
    start_page: int = 1
    end_page: int = 0  # 2564
    start_time = datetime
    processed_pages: int = 0
    movie_list_node: Node
    movie_list: list[SearchResult] = []
    search_type: SearchType
    movie_list_tuple: list[
        tuple[str, str | None, str | None, str | None, str | None, int]
    ] = []
    movie_insert_query: str = (
        "INSERT INTO movies (title, year, rating, poster_url, page_url, search_page_num) VALUES "
        "(?, ?, ?, ?, ?, ?)"
    )
    series_insert_query: str = (
        "INSERT INTO tv_series (title, year, rating, poster_url, page_url, search_page_num) VALUES "
        "(?, ?, ?, ?, ?, ?)"
    )
    database_connection: sqlite3.Connection
    database_name: str = "movies.db"

    def __init__(
        self, database_name, search_type: SearchType, start_page=1, end_page=0
    ):
        self.start_page = start_page
        self.end_page = end_page
        self.search_type = search_type
        self.database_name = database_name
        self.database_connection = sqlite3.connect(self.database_name)
        self.cursor = self.database_connection.cursor()
        self.session = httpx.Client()

    def _get_home_page(self):
        return self.session.get(self.home_page_url)

    def start_scraping_test(self):
        html = open("search_page.html").read()
        self.get_movie_list_node(html)
        for movie_node in self.movie_list_node.iter():
            self.movie_list.append(SearchResult(movie_node, 0))
        # pprint(self.movie_list)
        self.dump_scrape_status()

    def start_scraping(self):
        self.start_time = datetime.now()
        self._get_home_page()
        for page_num in range(self.start_page, self.end_page + 1):
            self.get_episode(page_num)
        self.dump_scrape_status()

    def get_episode(self, page_num: int):
        self.current_page = page_num
        current_page_url = self.base_search_url.format(
            search_type=self.search_type.value, page=page_num
        )
        pprint(f"fetching {current_page_url}")
        try:
            current_page_content = self.session.get(current_page_url)
            pprint(f"status code: {current_page_content.status_code}")
            self.get_movie_list_node(current_page_content.content)
            for movie_node in self.movie_list_node.iter():
                self.movie_list.append(SearchResult(movie_node, self.current_page))
            self.processed_pages += 1
        except Exception as e:
            print("Encountered exception ", e)
            print(f"Dumping scraped information to {self.database_name} and exiting")
            self.dump_scrape_status()
            exit(1)

    def dump_scrape_status(self):
        for movie in self.movie_list:
            self.movie_list_tuple.append(movie.to_tuple())
        if self.search_type == SearchType.MOVIE:
            self.cursor.executemany(self.movie_insert_query, self.movie_list_tuple)
        else:
            self.cursor.executemany(self.series_insert_query, self.movie_list_tuple)
        self.database_connection.commit()
        self.database_connection.close()
        with open("num_pages_scraped.txt", "w") as f:
            f.write(str(self.current_page))
        print(
            f"scraped {len(self.movie_list)} movies from {self.processed_pages} pages in "
            + f"{datetime.now() - self.start_time}"
        )
        print(f"Dumped movie info to '{self.database_name}'")
        print("dumped number of scraped pages to num_pages_scraped.txt")

    def get_movie_list_node(self, html: str | bytes) -> Node:
        tree = HTMLParser(html)
        self.movie_list_node = tree.css_first(".flex-wrap-movielist")
        return self.movie_list_node


def main():
    # scraper = Scraper("test_movies.db")
    # scraper.start_scraping_test()
    scraper = Scraper("tv_series.db", SearchType.SERIES, 1, 473)
    scraper.start_scraping()


if __name__ == "__main__":
    main()
