import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

MINS = 24*60
df = pd.read_csv("data/kicount_old_middleJuly.csv", names=["count", "total", "hour", "minute", "wday", "day", "month"])
df["daymin"] = (60*df["hour"] + df["minute"])/MINS


def get_weekday_data(wday="MO"):
    return df.loc[df["wday"] == wday, ["count", "daymin"]]


def get_fourier_formula(deg=3):
    # To make sure the predictions are >= 0 we model log(count+1)
    form = "np.log(count+1) ~ "
    for i in range(1, deg+1):
        form += "np.cos(" + str(i) + "*daymin) + "
        # Check for last degree to avoid hanging + sign at end of formula
        if i == deg:
            form += "np.sin(" + str(i) + "*daymin)"
        else:
            form += "np.sin(" + str(i) + "*daymin) + "
    return form


def quantile_prediction(wday="MO", deg=3):
    data = get_weekday_data(wday=wday)
    form = get_fourier_formula(deg=deg)
    mod = smf.quantreg(form, data=data)
    res = pd.DataFrame({"daymin": np.linspace(0, 1, MINS)})
    for q, name in zip([0.05, 0.25, 0.5, 0.75, 0.95], ["q5", "q25", "q50", "q75", "q95"]):
        quantile_model = mod.fit(q=q)
        # Return the count rather than prediciton of log(x+1)
        ys = np.exp(quantile_model.predict(res["daymin"])) - 1
        res[name] = ys
    return res


def plot_quantile(quantiles):
    fig, axs = plt.subplots()
    axs.plot(quantiles["daymin"], quantiles["q50"], color="blue")
    axs.fill_between(quantiles["daymin"], y1=quantiles["q5"], y2=quantiles["q95"], color="blue", alpha=0.1)
    axs.fill_between(quantiles["daymin"], y1=quantiles["q25"], y2=quantiles["q75"], color="blue", alpha=0.3)
    axs.set_ylim(bottom=-5, top=350)
    axs.set_xlabel("Hour")
    axs.set_ylabel("Count")
    axs.set_xticks(np.linspace(0, 1, 24))
    axs.set_xticklabels(np.arange(0, 24))
    return fig


monday = quantile_prediction(deg=5)
plot_quantile(monday)
