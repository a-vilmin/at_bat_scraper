# MLB AtBat Scraper 
Python script for scraping AtBat XML into a DB

# To get it running

So first clone the repo and init a Python3 virtual env. Install the `requirements.txt` file to your venv and get whatever DB you want to put the info into setup with the sqlAlchemy `Pitch.py` model (you can just do tthat in the interpretor, I haven't written any scripts for that). 

Once you have all that, to run, execute `python atbat_scraper.py <database URI> <("daily"|"full")>`. The scraper can either gather the previous day's games ("daily") or run from yesterday until the start of AtBat. Feel free to edit the times you want to scrape in the code, its pretty self explanitory.  

# HELPFUL LINKS

[Table for referencing player ID's](http://crunchtimebaseball.com/baseball_map.html)

[SQLAlchemy URI reference](https://docs.sqlalchemy.org/en/13/core/engines.html)

[Root page for AtBat XML](https://gd2.mlb.com/components/game/mlb/)
