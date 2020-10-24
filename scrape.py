import requests
from bs4 import BeautifulSoup
import datetime
import time


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

    return hour, mins, ["MO", "DI", "MI", "DO", "FR", "SA", "SO"][day]


wait_time = 600  # waiting time in seconds
f = open("kicount.txt", "w")

print("Start scraping!")

while True:

    time.sleep(wait_time)

    current, total = get_current()
    hour, mins, day = get_time()
    line = [current, total, hour, mins, day]
    line_str = ','.join((str(l) for l in line))

    f.write(line_str)
    f.writelines("\n")
    f.flush()
    print("Got new datapoint.")

f.close()
