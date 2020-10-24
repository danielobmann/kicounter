import numpy as np
import matplotlib.pyplot as plt


class Regression:
    """Implements a class for solving simple regression problems."""
    def __init__(self, formula, data):
        self.data = data
        self.formula = formula
        self.split = formula.split("~")
        self.response = formula[0].strip()
        self.covariate = formula[1].strip()

    @staticmethod
    def get_design_matrix(xs, mod="spline", deg=3, knots=4):
        """Set up a design matrix for the model."""
        if mod == "spline":
            dim = deg + knots - 1
            X = np.ones((len(xs), dim))
            knots = np.linspace(np.amin(xs), np.amax(xs), knots)

            for i in range(dim):
                if i <= deg:
                    X[..., i] = np.maximum(xs - knots[0], 0) ** i
                else:
                    X[..., i] = np.maximum(xs - knots[i - deg], 0) ** deg

        elif mod == "fourier":
            X = np.ones((len(xs), 2 * deg - 1))
            period = np.amax(xs) - np.amin(xs)
            for i in range(1, deg + 1):
                X[..., 2 * i - 1] = np.cos(i * xs * 2 * np.pi / period)
                X[..., 2 * i] = np.sin(i * xs * 2 * np.pi / period)

        else:
            raise Exception("Model not implemented")

        return X

    def ols(self, mod="spline"):
        X = self.get_design_matrix(self.data[self.covariate], mod=mod)
        y = self.data[self.response]
        beta = np.linalg.solve(X.T @ X, X.T @ y)
        return beta

