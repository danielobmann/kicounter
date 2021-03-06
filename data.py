import numpy as np
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import ast

import config


def robust_temp(month, year):
    https = "https://www.timeanddate.de/wetter/oesterreich/innsbruck/rueckblick?month=%d&year=%d" % (month, year)
    page = requests.get(https)
    soup = BeautifulSoup(page.text, 'html.parser')

    data = soup.find_all("script", {"type": "text/javascript"})[1]
    d = data.contents[0].split("data=")[1]
    d = d.split('"temp":[')[1]
    d = d.split("detail")
    temp = d[0].replace('],"', "")
    detail = d[1].split(',"grid"')[0].replace('":[', '[').replace('true', '1')

    temp = ast.literal_eval(temp)
    detail = ast.literal_eval(detail)
    return temp, detail


def get_temp(month):
    ret = {"year": [], "month": [], "day": [], "hour": [], "temp": []}
    for d in month:
        date = datetime.utcfromtimestamp(d["date"]/1000)
        ret["month"].append(int(date.strftime("%m")))
        ret["day"].append(int(date.strftime("%d")))
        ret["hour"].append(int(date.strftime("%H")))
        ret["year"].append(int(date.strftime("%Y")))
        try:
            ret["temp"].append(d["temp"])
        except:
            ret["temp"].append(-99)
    return pd.DataFrame(ret)


def month_to_int(month):
    months = {"Januar": 1,
              "Februar": 2,
              "März": 3,
              "April": 4,
              "Mai": 5,
              "Juni": 6,
              "Juli": 7,
              "August": 8,
              "September": 9,
              "Oktober": 10,
              "November": 11,
              "Dezember": 12}
    return months[month]


def convert_ds(ds):
    l = ds.split(',')
    wday = l[0].upper()[:2]
    day = int(l[1].split('.')[0].strip())
    month = month_to_int(l[1].split(' ')[2])
    year = int(l[1].split(' ')[-1])
    hours = [h.strip() for h in l[2].split(' ')]
    hours = [int(h.split(':')[0]) for h in hours if ':' in h]
    if hours[1] == 0:
        hours = [i for i in range(hours[0], 24)]
    else:
        hours = [i for i in range(hours[0], hours[1])]
    return wday, day, month, hours, year


def get_details(detail):
    wday, day, month, hours, year = convert_ds(detail['ds'])
    N = len(hours)
    try:
        temp = detail['temp']
    except:
        temp = -99

    res = pd.DataFrame({'wday': N*[wday],
                        'day': N*[day],
                        'month': N*[month],
                        'year': N*[year],
                        'hour': hours,
                        'temp': N*[temp],
                        'humidity': N*[detail['hum']],
                        'description': N*[detail['desc']],
                        'baro': N*[detail['baro']]})
    return res


def get_all(temp, details):
    df_temp = get_temp(temp)
    df_detail = pd.DataFrame()
    for detail in details:
        df_detail = df_detail.append(get_details(detail), ignore_index=True)

    merge_on = ['year', 'month', 'day', 'hour']
    df = pd.merge(df_detail, df_temp,  how='left', left_on=merge_on, right_on=merge_on)

    # Replace missing temperature
    replace = df["temp_y"].isna()
    df.loc[replace, "temp_y"] = df.loc[replace, "temp_x"]

    df = df.drop("temp_x", axis=1)
    df = df.rename(columns={'temp_y': 'temp'})
    return df


def read_data(path=config.vars["scrape_path"]):
    data = pd.read_csv(path, names=["count", "total", "hour", "minute", "wday", "day", "month", "year"])
    data["daymin"] = (60 * data["hour"] + data["minute"]) / config.vars["mins"]
    return data


def merge_data(path=config.vars["scrape_path"], year=2020):
    ki = read_data(path=path)

    months = set(ki['month'])
    df_new = pd.DataFrame()

    for month in months:
        temp, det = robust_temp(month=month, year=year)
        df_new = df_new.append(get_all(temp, det), ignore_index=True)

    merge_on = ['month', 'day', 'hour', 'wday']
    df = pd.merge(ki, df_new, how='left', left_on=merge_on, right_on=merge_on)
    return df


try:
    df = pd.read_csv(config.vars["path"], index_col=0)
except:
    df = merge_data()
    df.to_csv(config.vars["path"])


def get_weekday_data(df=df, wday="MO", beg=config.vars["opening"], end=config.vars["closing"], scale=True):
    data = df.loc[(df["wday"] == wday) & (df["hour"] < end) & (df["hour"] >= beg), ]
    if scale:
        m = np.amin(data["daymin"])
        M = np.amax(data["daymin"])
        data.loc[:, "daymin"] = (data.loc[:, "daymin"] - m)/(M - m)
    return data
