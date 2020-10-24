# -----------------
# Import libraries
import statsmodels.api as sm
import matplotlib.pyplot as plt
import os

from formulas import *
from data import *

# -----------------
# Set up functions


def plot_quantile(wday, quantiles, beg=config.vars["opening"], end=config.vars["closing"], save=True):
    fig, axs = plt.subplots()
    axs.plot(quantiles["daymin"], quantiles["q50"], color="blue")
    axs.fill_between(quantiles["daymin"], y1=quantiles["q5"], y2=quantiles["q95"], color="blue", alpha=0.1)
    axs.set_ylim(bottom=config.vars["minimum"] - 5, top=config.vars["maximum"])
    axs.set_xlabel("Hour")
    axs.set_ylabel("Count")
    axs.set_xticks(np.linspace(0, 1, end - beg + 1))
    axs.set_xticklabels(np.arange(beg, end+1))
    axs.set_title(wday)
    if save:
        plt.savefig(config.vars["img_path"] + wday + ".pdf")
    plt.clf()
    pass


def quantile_model(wday="MO", mod="spline", save=True, **kwargs):
    data = get_weekday_data(wday=wday)
    form = get_formula(mod=mod, **kwargs)
    mod = sm.formula.quantreg(form, data=data)
    res = pd.DataFrame({"daymin": np.linspace(0, 1, config.vars["mins"])})
    for q, name in zip([0.05, 0.5, 0.95], ["q5", "q50", "q95"]):
        qm = mod.fit(q=q, max_iter=5000)
        ys = qm.predict(res["daymin"])
        res[name] = ys

        if save:
            path = os.path.join(config.vars["model_path"], wday)
            if not os.path.exists(path):
                os.mkdir(path)

            qm.save(os.path.join(path, name + ".pickle"))

    print("Models fitted.")
    plot_quantile(wday=wday, quantiles=res)
    return res


if __name__ == '__main__':

    RES = {}
    for wday in ["MO", "DI", "MI", "DO", "FR", "SA", "SO"]:
        res = quantile_model(wday=wday, deg=5)
        RES[wday] = res["q50"]
        RES["xs"] = res["daymin"]

    fig, axs = plt.subplots()

    for wday in ["MO", "DI", "MI", "DO", "FR", "SA", "SO"]:
        axs.plot(RES["xs"], RES[wday], label=wday)

    axs.set_ylim(bottom=config.vars["minimum"] - 5, top=config.vars["maximum"])
    axs.set_xlabel("Hour")
    axs.set_ylabel("Count")
    axs.set_xticks(np.linspace(0, 1, config.vars["closing"] - config.vars["opening"] + 1))
    axs.set_xticklabels(np.arange(config.vars["opening"], config.vars["closing"] + 1))
    axs.legend()
    axs.set_title("Weekdays")
    plt.savefig(config.vars["img_path"] + "week.pdf")
    plt.clf()
