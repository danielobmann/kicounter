import pandas as pd
import numpy as np

import config


def read_data(path=config.vars["path"]):
    data = pd.read_csv(path, names=["count", "total", "hour", "minute", "wday", "day", "month"])
    data["daymin"] = (60 * data["hour"] + data["minute"]) / config.vars["mins"]
    return data


df = read_data()


def get_weekday_data(wday="MO", beg=config.vars["opening"], end=config.vars["closing"], scale=True):
    data = df.loc[(df["wday"] == wday) & (df["hour"] < end) & (df["hour"] >= beg), ["count", "daymin"]]
    if scale:
        m = np.amin(data["daymin"])
        M = np.amax(data["daymin"])
        data["daymin"] = (data["daymin"] - m)/(M - m)
    return data
