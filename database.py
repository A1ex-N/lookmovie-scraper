import enum
import logging
import os
import sqlite3

from search_result import SearchResult


class CreationQueries(enum.Enum):
    """enum containing SQL queries for creating tables in a db"""

    MOVIES = "CREATE TABLE movies (title, year, rating, poster_url, page_url, search_page_num)"
    SERIES = "CREATE TABLE tv_series (title, year, rating, poster_url, page_url, search_page_num)"


class InsertionQueries(enum.Enum):
    """enum containing SQL queries for inserting to a db"""

    MOVIES = """
        INSERT INTO movies (title, year, rating, poster_url, page_url, search_page_num) VALUES 
        (?, ?, ?, ?, ?, ?)
        """
    SERIES = """
        INSERT INTO tv_series (title, year, rating, poster_url, page_url, search_page_num) VALUES 
        (?, ?, ?, ?, ?, ?)
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
        if not self.already_exists:
            self.create_tables()

    def create_tables(self):
        """creates tables from CreationQueries.MOVIES and CreationQueries.SERIES"""
        logging.info("creating tables in %s", self.database_path)
        self.cursor.execute(CreationQueries.SERIES.value)
        self.cursor.execute(CreationQueries.MOVIES.value)
        self.connection.commit()

    def insert_new_movies(self, search_results: list[tuple[SearchResult]]):
        """
        Inserts movies into movies table

        :param search_results: List of tuples of SearchResults
        """
        logging.info("inserting movies into %s", self.database_path)
        self.cursor.executemany(InsertionQueries.MOVIES.value, search_results)
        self.connection.commit()

    def insert_new_series(self, search_results: list[tuple[SearchResult]]):
        """
        Inserts series into tv_series table

        :param search_results: List of tuples of SearchResults
        """
        logging.info("inserting series into %s", self.database_path)
        self.cursor.executemany(InsertionQueries.SERIES.value, search_results)
        self.connection.commit()

    def close(self):
        """closes database connection"""
        logging.info("closing %s", self.database_path)
        self.connection.close()
