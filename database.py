import enum
import logging
import os
import sqlite3

from search_result import SearchResult


def generate_sql_table(table_name: str) -> str:
      return f"""CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(255) NOT NULL,
            year INT,
            rating INT,
            poster_url VARCHAR(255),
            page_url VARCHAR(255),
            search_page_num INT,
            search_query VARCHAR(255),
            scraped_at_utc DATETIME DEFAULT CURRENT_TIMESTAMP
        )"""


class CreationQueries(enum.Enum):
    """enum containing SQL queries for creating tables in a db"""
    MOVIES = generate_sql_table("movies")
    SERIES = generate_sql_table("tv_series")


class InsertionQueries(enum.Enum):
    """enum containing SQL queries for inserting to a db"""

    MOVIES = """
        INSERT INTO movies (title, year, rating, poster_url, page_url, search_page_num, search_query) VALUES 
        (?, ?, ?, ?, ?, ?, ?)
        """
    SERIES = """
        INSERT INTO tv_series (title, year, rating, poster_url, page_url, search_page_num, search_query) VALUES 
        (?, ?, ?, ?, ?, ?, ?)
        """


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

    def insert_new_movies(self, search_results: list[tuple[SearchResult]]):
        """
        Inserts movies into movies table

        :param search_results: List of tuples of SearchResults
        """
        logging.info("inserting movies into %s", self.database_path)
        self.cursor.execute(CreationQueries.MOVIES.value)
        self.cursor.executemany(InsertionQueries.MOVIES.value, search_results)
        self.connection.commit()

    def insert_new_series(self, search_results: list[tuple[SearchResult]]):
        """
        Inserts series into tv_series table

        :param search_results: List of tuples of SearchResults
        """
        logging.info("inserting series into %s", self.database_path)
        self.cursor.execute(CreationQueries.MOVIES.value)
        self.cursor.executemany(InsertionQueries.SERIES.value, search_results)
        self.connection.commit()

    def close(self):
        """closes database connection"""
        logging.info("closing %s", self.database_path)
        self.connection.close()
