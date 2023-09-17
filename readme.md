initialize Scraper with the database name, start page and end page (inclusive)
Note you have to manually create the db file. I do that by running `sqlite3 -init movies_schema.sql` then typing 
`.save movies.db` followed by `quit`
```python
def main():
    scraper = Scraper("movies.db", start_page=201, end_page=300)
    scraper.start_scraping()
```
It'll start going through all the search result pages (https://lookmovie2.to/movies/search/page/{page}?q=) starting at 
`start_page` and ending at `end_page` (inclusive). You could change `base_search_url` in scraper.py to search for 
something specific and only scrape those pages if you want.

I'm pretty sure i've done many things in this script very inefficiently, it takes about 1 second per page to scrape 
information, and at the time of writing this there's currently 2564 pages for movie search results.