"""Sign-constrained L2 logistic regression: symptoms, cough duration, TB history, CRP and CAD cannot lower the risk.
Why: in the open data everyone was selected for TB-like symptoms or an abnormal X-ray, which can make a symptom look protective
(for example weight loss with a negative coefficient). A model that says 'weight loss lowers TB risk' is wrong for a clinician and breaks the SHAP story.
Sex and age are left free (the data decides)."""
import numpy as np
from scipy.optimize import minimize

NONNEG = {"cough", "fever", "chestpain", "nightsweats", "weightlost", "cough_dur", "prior_tb", "crp_log2", "cad", "xray_prob"}


class ConLR:
    def __init__(self, cols, C=0.3, constrain=True): self.cols, self.C, self.constrain = cols, C, constrain

    def fit(self, X, y):
        self.mean_, self.scale_ = X.mean(0), X.std(0) + 1e-9; Z = (X - self.mean_) / self.scale_; n, k = Z.shape; y = y.astype(float)
        def f(w):
            b, v = w[0], w[1:]; z = Z @ v + b; ll = np.logaddexp(0, z) - y * z; p = 1 / (1 + np.exp(-z)); r = p - y
            return ll.sum() + 0.5 / self.C * (v @ v), np.concatenate([[r.sum()], Z.T @ r + v / self.C])
        bounds = [(None, None)] + [((0, None) if (self.constrain and c in NONNEG) else (None, None)) for c in self.cols]
        res = minimize(f, np.zeros(k + 1), jac=True, method="L-BFGS-B", bounds=bounds)
        self.intercept_, self.coef_ = res.x[0], res.x[1:]; return self

    def predict_proba(self, X):
        z = ((X - self.mean_) / self.scale_) @ self.coef_ + self.intercept_; p = 1 / (1 + np.exp(-z)); return np.c_[1 - p, p]
