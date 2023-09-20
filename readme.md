This repo already contains complete database files in the /database folder, but if you want to run the code yourself continue reading 

you can run it by doing `python scraper.py` or if you wanted to use it in your own code do it like so

initialize Scraper with the `database_name`, `search_type`, `start_page` and `end_page` (inclusive)
```python
def main():
    scraper = Scraper(database_name="movies.db", search_type=SearchType.MOVIE, start_page=201, end_page=300)
    scraper.start_scraping()
```
It'll start going through all the search result pages (https://lookmovie2.to/movies/search/page/{page}?q=) starting at 
`start_page` and ending at `end_page` (inclusive). You could change `base_search_url` in scraper.py to search for 
something specific and only scrape those pages if you want.

`search_type` can be `SearchType.MOVIE` or `SearchType.SERIES`

It takes about 1 second per page to scrape 
information, and at the time of writing this there's currently 2564 pages for movie search results and 473 pages for 
TV series. There's 20 results per page.

This repo contains complete databases for movies and TV series as of 18/09/2023.
