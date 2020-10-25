import requests
from bs4 import BeautifulSoup
import datetime
import time

import config


def get_current():
    page = requests.get("https://www.kletterzentrum-innsbruck.at/")
    soup = BeautifulSoup(page.text, 'html.parser')

    counter = soup.find_all("div", {"id": "main"})[0].find_all("div", {"class": "bold"})[0]
    current = int(counter.get_text().split("%")[1].split("/")[0])
    total = int(counter.get_text().split("%")[1].split("/")[1])

    return current, total


def get_time():
    now = datetime.datetime.now()
    day = now.weekday()
    hour = now.time().hour
    mins = now.time().minute
    dday = now.day
    month = now.month
    year = now.year

    return hour, mins, ["MO", "DI", "MI", "DO", "FR", "SA", "SO"][day], dday, month, year


# Define waiting time in seconds
wait_time = 600

while True:

    current, total = get_current()
    hour, mins, day, dday, month, year = get_time()
    line = [current, total, hour, mins, day, dday, month, year]
    line_str = ','.join((str(l) for l in line))

    f = open(config.vars["scrape_path"], "a")
    f.write(line_str)
    f.writelines("\n")
    f.flush()
    f.close()
    print("Got new datapoint, waiting %ds" % wait_time)

    time.sleep(wait_time)
