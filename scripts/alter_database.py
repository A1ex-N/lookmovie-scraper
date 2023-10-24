"""
the original db schema i went with used an autoincrementing int as the primary key,
but i decided i no longer wanted it like that. This script replaces 'id' with 
a primary text key named 'slug', which is just the 'page_url' with everything before the last 
forward slash. Any duplicate data (page_url) gets removed too.
"""



import sqlite3


DATABASE_PATH = "./database/scraped_data.db"


def generate_sql(table_name: str) -> str:
    return f"""
    CREATE TABLE {table_name} (
        slug TEXT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        year INT,
        rating INT,
        poster_url VARCHAR(255),
        page_url VARCHAR(255),
        search_page_num INT,
        scraped_at_utc DATETIME DEFAULT CURRENT_TIMESTAMP,
        search_query VARCHAR(255)
    );"""


def generate_insert_sql(table_name: str) -> str:
    return f"""
    INSERT OR IGNORE INTO {table_name} (slug, title, year, rating, poster_url, page_url, search_page_num, scraped_at_utc, search_query)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """


def update_all(items):
    for item in items:
        updated = list(item)
        updated[0] = updated[5].split('/')[-1]
        yield tuple(updated)


def drop_and_rename(cursor: sqlite3.Cursor, to_remove: str, to_rename: str):
    """
    Drops (deletes) table `to_remove` and renames
    `to_rename` to `to_remove`
    """

    remove_sql = f"""
        DROP TABLE {to_remove};
        ALTER TABLE {to_rename} RENAME TO {to_remove};
    """
    cursor.execute(remove_sql)


if __name__ == "__main__":
    original_table = "tv_series"
    new_table = "tv_series_new"
    remove_original = False

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    
    res = cursor.execute(f"SELECT * FROM {original_table}")
    all = res.fetchall()

    updated = list(update_all(all))

    cursor.execute(generate_sql(new_table))
    cursor.executemany(generate_insert_sql(new_table), updated)

    if remove_original:
        drop_and_rename(cursor, original_table, new_table)

    connection.commit()
