from search_result import SearchResult
import logging
import sqlite3
import enum
import os


class CreationQueries(enum.Enum):
    movies = "CREATE TABLE movies (title, year, rating, poster_url, page_url, search_page_num)"
    series = "CREATE TABLE tv_series (title, year, rating, poster_url, page_url, search_page_num)"


class InsertionQueries(enum.Enum):
    movies = """
        INSERT INTO movies (title, year, rating, poster_url, page_url, search_page_num) VALUES 
        (?, ?, ?, ?, ?, ?)
        """
    series = """
        INSERT INTO tv_series (title, year, rating, poster_url, page_url, search_page_num) VALUES 
        (?, ?, ?, ?, ?, ?)
        """


class Database:
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
        logging.log(logging.INFO, f"creating tables in {self.database_path}")
        self.cursor.execute(CreationQueries.series.value)
        self.cursor.execute(CreationQueries.movies.value)
        self.connection.commit()

    def insert_new_movies(self, search_results: list[tuple[SearchResult]]):
        logging.log(logging.INFO, f"inserting movies into {self.database_path}")
        self.cursor.executemany(InsertionQueries.movies.value, search_results)
        self.connection.commit()

    def insert_new_series(self, search_results: list[tuple[SearchResult]]):
        logging.log(logging.INFO, f"inserting series into {self.database_path}")
        self.cursor.executemany(InsertionQueries.series.value, search_results)
        self.connection.commit()

    def close(self):
        logging.log(logging.INFO, f"closing {self.database_path}")
        self.connection.close()