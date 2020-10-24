# -----------------
# Import libraries
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

from formulas import *
from data import *

# -----------------
# Set up functions


def quantile_prediction(wday="MO", deg=3, beg=config.vars["opening"], end=config.vars["closing"], mod="spline"):
    data = get_weekday_data(wday=wday, beg=beg, end=end, scale=True)
    form = get_formula(mod=mod, deg=deg)
    mod = smf.quantreg(form, data=data)
    res = pd.DataFrame({"daymin": np.linspace(0, 1, config.vars["mins"])})
    for q, name in zip([0.05, 0.5, 0.95], ["q5", "q50", "q95"]):
        quantile_model = mod.fit(q=q)
        ys = quantile_model.predict(res["daymin"])
        res[name] = ys
    return res


def plot_quantile(quantiles, beg=config.vars["opening"], end=config.vars["closing"]):
    fig, axs = plt.subplots()
    axs.plot(quantiles["daymin"], quantiles["q50"], color="blue")
    axs.fill_between(quantiles["daymin"], y1=quantiles["q5"], y2=quantiles["q95"], color="blue", alpha=0.1)
    axs.set_ylim(bottom=config.vars["minimum"] - 5, top=config.vars["maximum"])
    axs.set_xlabel("Hour")
    axs.set_ylabel("Count")
    axs.set_xticks(np.linspace(0, 1, end - beg + 1))
    axs.set_xticklabels(np.arange(beg, end+1))
    return fig


monday = quantile_prediction(mod="spline", deg=5)
plot_quantile(monday)
