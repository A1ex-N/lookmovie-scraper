CREATE TABLE IF NOT EXISTS movies (
    slug TEXT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    year INT,
    rating INT,
    poster_url VARCHAR(255),
    page_url VARCHAR(255),
    search_page_num INT,
    scraped_at_utc DATETIME DEFAULT CURRENT_TIMESTAMP,
    search_query VARCHAR(255)
);
