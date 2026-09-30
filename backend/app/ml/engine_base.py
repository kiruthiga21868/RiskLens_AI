"""
Shared ML building blocks.

WHY A WEIGHTED LOGISTIC MODEL
    Every threat detector renders an interpretable, weighted risk score.
    We materialise that score as a scikit-learn LogisticRegression whose
    coefficients ARE the domain weights. This gives us:
        - real probability + confidence (predict_proba),
        - a genuine sklearn model for SHAP (LinearExplainer is exact),
        - feature importance that exactly matches the security heuristics,
        - determinism (no stochastic training, no drift).

WHY THIS IS STILL "MACHINE LEARNING"
    The weights are the learned decision boundary of a logistic model.
    Later sprints can replace these coefficients with ones fitted on real
    datasets (see notebooks/), and the API/explainability layer is unchanged.
"""
from typing import Sequence

import numpy as np
from sklearn.linear_model import LogisticRegression

FEATURE_FLOOR = 0.0001


def build_weighted_model(feature_names: Sequence[str], weights: Sequence[float]) -> LogisticRegression:
    """
    Build a LogisticRegression whose decision boundary is exactly `weights`.

    We inject coefficients directly (coef_/intercept_/classes_) so that
    predict_proba returns sigmoid(X @ weights), and SHAP LinearExplainer
    attributes each prediction to the features with exact contributions.
    """
    model = LogisticRegression()
    model.classes_ = np.array([0, 1])
    model.coef_ = np.array([weights], dtype=float)
    model.intercept_ = np.array([0.0])
    return model


def build_explanations(model: LogisticRegression, feature_names: Sequence[str],
                       x_row: list[float]) -> dict[str, float]:
    """
    Compute exact linear-SHAP contributions for one feature row.

    For a logistic model this reduces to
        contribution_i = coef_i * (x_i - baseline_i),
    which shap.LinearExplainer returns exactly and instantly.
    """
    import shap  # imported lazily to keep startup lean

    baseline = np.ones((1, len(feature_names))) * 0.5
    explainer = shap.LinearExplainer(model, baseline)
    values = explainer.shap_values(np.asarray(x_row, dtype=float).reshape(1, -1))
    # values is shape (1, n_features) for binary logistic
    return {name: float(v) for name, v in zip(feature_names, values.reshape(-1))}
