from enum import Enum
import logging
import os
import sqlite3

from search_result import SearchResult
from search_types import SearchType


def generate_sql_table(table_name: str) -> str:
    return f"""CREATE TABLE IF NOT EXISTS {table_name} (
            slug TEXT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            year INT,
            rating INT,
            poster_url VARCHAR(255),
            page_url VARCHAR(255),
            search_page_num INT,
            scraped_at_utc DATETIME,
            search_query VARCHAR(255)
        )"""


def generate_insertion_query(table_name: str):
    return f"""
        INSERT OR IGNORE INTO {table_name}
        (slug, title, year, rating, poster_url, page_url, search_page_num, scraped_at_utc, search_query)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """


class CreationQueries(Enum):
    """enum containing SQL queries for creating tables in a db"""

    MOVIES = generate_sql_table("movies")
    SERIES = generate_sql_table("tv_series")


class InsertionQueries(Enum):
    """enum containing SQL queries for inserting to a db"""

    MOVIES = generate_insertion_query("movies")
    SERIES = generate_insertion_query("tv_series")


class Database:
    """
    simple class for handling a sqlite database
    """

    database_path: str
    connection: sqlite3.Connection
    cursor: sqlite3.Cursor
    already_exists: bool

    def __init__(self, path: str):
        self.database_path = path
        self.already_exists = os.path.exists(path)
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()

    def insert_search_results(
        self, search_results: list[tuple[SearchResult]], table_type: SearchType
    ):
        """
        Inserts search results into table

        :param search_results: List of tuples of SearchResults
        """
        logging.info("inserting %s into %s", table_type.value, self.database_path)
        # There's no particular reason the default is series
        creation_query = CreationQueries.SERIES.value
        insertion_query = InsertionQueries.SERIES.value
        if table_type == SearchType.MOVIE:
            creation_query = CreationQueries.MOVIES.value
            insertion_query = InsertionQueries.MOVIES.value
        self.cursor.execute(creation_query)
        self.cursor.executemany(insertion_query, search_results)
        self.connection.commit()

    def close(self):
        """closes database connection"""
        logging.info("closing %s", self.database_path)
        self.connection.close()
