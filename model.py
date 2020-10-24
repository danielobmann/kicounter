# -----------------
# Import libraries
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

# -----------------
# Global variables
MINS = 24 * 60
MIN = 0
MAX = 350
OPENING = 9
CLOSING = 22

# -----------------
# Set up functions


def read_data(path="data/kicount_old_middleJuly.csv"):
    data = pd.read_csv(path, names=["count", "total", "hour", "minute", "wday", "day", "month"])
    data["daymin"] = (60 * data["hour"] + data["minute"]) / MINS
    return data


df = read_data()


def get_weekday_data(wday="MO", beg=OPENING, end=CLOSING, scale=True):
    data = df.loc[(df["wday"] == wday) & (df["hour"] < end) & (df["hour"] >= beg), ["count", "daymin"]]
    if scale:
        m = np.amin(data["daymin"])
        M = np.amax(data["daymin"])
        data["daymin"] = (data["daymin"] - m)/(M - m)
    return data


def get_fourier_formula(deg=3):
    """Set up a cut-off Fourier series where we assume $x \\in [0,1]$"""
    form = "count ~ "
    for i in range(1, deg+1):
        form += "np.cos(2*np.pi*daymin*" + str(i) + ") + "
        # Check for last degree to avoid hanging + sign at end of formula
        if i == deg:
            form += "np.sin(2*np.pi*daymin*" + str(i) + ")"
        else:
            form += "np.sin(2*np.pi*daymin*" + str(i) + ") + "
    return form


def quantile_prediction(wday="MO", deg=3, beg=OPENING, end=CLOSING):
    data = get_weekday_data(wday=wday, beg=beg, end=end, scale=True)
    form = get_fourier_formula(deg=deg)
    mod = smf.quantreg(form, data=data)
    res = pd.DataFrame({"daymin": np.linspace(0, 1, MINS)})
    for q, name in zip([0.05, 0.25, 0.5, 0.75, 0.95], ["q5", "q25", "q50", "q75", "q95"]):
        quantile_model = mod.fit(q=q)
        # Return the count rather than prediciton of log(x+1)
        ys = quantile_model.predict(res["daymin"])
        res[name] = ys
    return res


def plot_quantile(quantiles, beg=OPENING, end=CLOSING):
    fig, axs = plt.subplots()
    axs.plot(quantiles["daymin"], quantiles["q50"], color="blue")
    axs.fill_between(quantiles["daymin"], y1=quantiles["q5"], y2=quantiles["q95"], color="blue", alpha=0.1)
    axs.fill_between(quantiles["daymin"], y1=quantiles["q25"], y2=quantiles["q75"], color="blue", alpha=0.3)
    axs.set_ylim(bottom=MIN - 5, top=MAX)
    axs.set_xlabel("Hour")
    axs.set_ylabel("Count")
    axs.set_xticks(np.linspace(0, 1, end - beg + 1))
    axs.set_xticklabels(np.arange(beg, end+1))
    return fig


monday = quantile_prediction()
plot_quantile(monday)
