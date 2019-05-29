import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from models import Pitch, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import logging

# init logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler('scraper.log')
handler.setLevel(logging.INFO)

formatter = logging.Formatter(('%(asctime)s - %(name)s - ' +
                               '%(levelname)s - %(message)s'))
handler.setFormatter(formatter)

logger.addHandler(handler)


def parse_game(url, date):
    r = requests.get(url)
    if r.status_code != 200:
        logger.warning('URL %s did not connect', url)
        return
    soup = BeautifulSoup(r.text, 'html.parser')

    # actual inning numbers in the 1 to -3 range
    inning_links = [x.get('href') for x in soup.find_all('a')][1:-3]
    finished_all = True
    for inning in inning_links:
        try:
            inning = inning.split('/')[1]
        except IndexError:
            logger.error("Inning didnt split on %s", inning)
            pass

        r = requests.get(url+inning)
        if r.status_code != 200:
            logger.warning('URL %s did not connect', url)
            finished_all = False
            continue
        parse_inning(r, url+inning, date)
    if finished_all and len(inning_links) > 0:
        logger.info("Scraped %s thru %s", url, inning_links[-1])
    else:
        logger.warning("Check error log for missing inning")


def parse_inning(request, url, date):
        try:
            root = ET.fromstring(request.text)
            at_bats = [[e for e in side if e.tag == 'atbat'] for side in root]
        except ET.ParseError:
            logger.error("XML parsing error on %s", url)
            return

        for at_bat in sum(at_bats, []):
            pitches = [x for x in at_bat if x.tag == 'pitch']
            pitcher = int(at_bat.attrib['pitcher'])
            hitter = int(at_bat.attrib['batter'])
            stand = at_bat.attrib['stand']
            for pitch in pitches:
                pitch = pitch.attrib
                for key, value in pitch.items():
                    if value == "placeholder":
                        pitch[key] = 0
                try:
                    new_pitch = Pitch(pitcher=pitcher, hitter=hitter,
                                      date=date, stand=stand,
                                      outcome=pitch['des'],
                                      start_speed=float(pitch['start_speed']),
                                      end_speed=float(pitch['end_speed']),
                                      sz_top=float(pitch['sz_top']),
                                      sz_bot=float(pitch['sz_bot']),
                                      pfx_x=float(pitch['pfx_x']),
                                      pfx_z=float(pitch['pfx_z']),
                                      px=float(pitch['px']),
                                      pz=float(pitch['pz']),
                                      x0=float(pitch['x0']),
                                      z0=float(pitch['z0']),
                                      pitch_type=pitch['pitch_type'],
                                      zone=int(pitch['zone']),
                                      spin_dir=float(pitch['spin_dir']),
                                      spin_rate=float(pitch['spin_rate']))
                    session.add(new_pitch)
                    session.commit()
                except KeyError:
                    logger.error("Key Missing For %s", url, exc_info=True)
                    continue

def run_full_scrape():
    # creates full db from current date to 2008
    now = datetime(2011, 3, 20)
    end = datetime(2008, 1, 1)

    while now > end:
        year = now.year
        month = now.month
        day = now.day
        base_url = ("https://gd2.mlb.com/components/game/mlb/"
                    "year_{0}/month_{1:0>2}/day_{2:0>2}").format(year,
                                                                 month, day)

        r = requests.get(base_url)
        if r.status_code != 200:
            logger.warning('URL %s did not connect', base_url)
            now = now - timedelta(days=1)
            continue

        soup = BeautifulSoup(r.text, 'html.parser')
        games = [x.get('href') for x in soup.find_all('a')]
        games = [x for x in games if 'gid' in x]
        for game in games:
            url = ("https://gd2.mlb.com/components/game/mlb/"
                   "year_{0}/month_{1:0>2}/{2}inning/").format(year,
                                                               month, game)
            parse_game(url, now)

        logger.info("Scraped %s with %d games", base_url, len(games))
        now = now - timedelta(days=1)


def run_previous_day():
    now = datetime.now() - timedelta(days=1)
    year = now.year
    month = now.month
    day = now.day
    base_url = ("https://gd2.mlb.com/components/game/mlb/"
                "year_{0}/month_{1:0>2}/day_{2:0>2}").format(year,
                                                             month, day)

    r = requests.get(base_url)
    if r.status_code != 200:
        logger.warning('URL %s did not connect', base_url)
        return

    soup = BeautifulSoup(r.text, 'html.parser')
    games = [x.get('href') for x in soup.find_all('a')]
    games = [x for x in games if 'gid' in x]
    for game in games:
        url = ("https://gd2.mlb.com/components/game/mlb/"
               "year_{0}/month_{1:0>2}/{2}inning/").format(year,
                                                           month, game)
        parse_game(url, now)

    logger.info("Scraped %s with %d games", base_url, len(games))


if __name__ == '__main__':
    from sys import argv

    if len(argv) > 1:
        # init db stuff for SQLAlchemy 'sqlite:///pitch_fx.db'
        try:
            engine = create_engine(argv[1])
            Base.metadata.bind = engine
            DBSession = sessionmaker(bind=engine)
            session = DBSession()
        except:
            logger.error("Error connecting to DB %s", argv[1])

        if argv[2] == 'daily':
            run_previous_day()
        elif argv[2] == 'full':
            run_full_scrape()
        else:
            logger.error("Invalid command line argument %s", argv[2])
    else:
        print("Missing arguments. Need both DB connection path and runtype " +
              "(daily or full)")
