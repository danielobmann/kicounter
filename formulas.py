import numpy as np


def spline(x, deg, knot):
    return np.maximum(x - knot, 0)**deg


def get_formula(x="daymin", y="count", mod="spline", deg=3, knots=4):
    """Set up a design matrix for the model.
    The formulas assume that the values of x are in [0,1]."""
    form = y + " ~ "
    if mod == "spline":
        dim = deg + knots - 1
        knots = np.linspace(0, 1, knots)

        for i in range(1, dim):
            if i <= deg:
                form += "spline(%s, %d, %f) + " % (x, i, knots[0])
            else:
                if i == dim-1:
                    form += "spline(%s, %d, %f)" % (x, i, knots[i - deg])

                else:
                    form += "spline(%s, %d, %f) + " % (x, i, knots[i - deg])

    elif mod == "fourier":
        for i in range(1, deg):
            if i == deg - 1:
                form += "np.cos(%s * %d * %f) + np.sin(%s * %d * %f)" % (x, i, 2 * np.pi, x, i, 2 * np.pi)
            else:
                form += "np.cos(%s * %d * %f) + np.sin(%s * %d * %f) + " % (x, i, 2*np.pi, x, i, 2*np.pi)

    else:
        raise Exception("Model not implemented")

    return form
