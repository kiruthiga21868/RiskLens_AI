"""
Detection engine - URL, email and credential detectors.

Every detector returns a unified response with the SIX fields the whole
platform guarantees for every prediction:
    prediction, confidence, risk_score, feature_importance,
    explanation, recommendation.

Detectors share one base class that wraps a surrogate sklearn model and
SHAP so the explainable-AI logic is written exactly once (DRY + SOLID).
"""
from typing import Any

from app.core.config import get_settings
from app.ml.engine_base import build_explanations, build_weighted_model
from app.ml.url_features import extract_url_features

import math
import re

import numpy as np

_URGENT_WORDS = {"urgent", "free", "winner", "prize", "click", "now", "limited",
                 "offer", "congratulations", "claim", "verify", "suspended",
                 "cash", "million", "selected", "trial", "act", "immediately"}
_SPOOF_PROVIDERS = {"paypal", "ebay", "amazon", "facebook", "instagram", "whatsapp",
                    "google", "microsoft", "bank", "apple", "netflix", "crypto"}


class _BaseDetector:
    """Shared inference pipeline: features -> model -> SHAP -> unified output."""

    labels: tuple[str, str] = ("safe", "risky")  # (negative, positive)
    feature_names: list[str] = []
    weights: list[float] = []
    intercept: float = 0.0

    def __init__(self) -> None:
        self._model = None
        self._settings = get_settings()

    def model(self):
        if self._model is None:
            m = build_weighted_model(self.feature_names, self.weights)
            m.intercept_ = np.array([self.intercept]) if self.intercept else np.array([0.0])
            self._model = m
        return self._model

    def features_from(self, raw: str) -> dict[str, float]:
        raise NotImplementedError

    def predict_proba(self, raw: str) -> tuple[dict[str, float], float]:
        feats = self.features_from(raw)
        x = [feats[name] for name in self.feature_names]
        prob = float(self.model().predict_proba([x])[0][1])
        return feats, prob

    def analyze(self, raw: str, *, threshold: float | None = None) -> dict[str, Any]:
        feats, prob = self.predict_proba(raw)
        thr = threshold if threshold is not None else self._settings.HIGH_RISK_THRESHOLD

        risk_score = round(prob * 100, 1)
        prediction = self.labels[1] if prob >= thr else self.labels[0]
        confidence = round(max(prob, 1 - prob), 3)

        x = [feats[name] for name in self.feature_names]
        importance = build_explanations(self._model, self.feature_names, x)
        top = sorted(importance.items(), key=lambda kv: abs(kv[1]), reverse=True)[:6]

        return {
            "prediction": prediction,
            "confidence": confidence,
            "risk_score": risk_score,
            "feature_importance": importance,
            "explanation": self._explain(top, feats, prob),
            "recommendation": self.recommend(prob, prediction),
            "raw_score": round(prob, 4),
            "details": {"top_features": {k: round(v, 4) for k, v in top[:6]}},
        }

    @staticmethod
    def _explain(top: list[tuple[str, float]], feats: dict[str, float], prob: float) -> str:
        if not top:
            return "No strong features influenced this prediction."
        lead = top[0]
        parts = [
            f"The '{lead[0]}' signal was the strongest factor (contribution {lead[1]:+.2f}) "
            f"and raised/lowered the risk estimate to {prob:.0%}."
        ]
        for name, val in top[1:4]:
            parts.append(f"'{name}' contributed {val:+.2f}.")
        return " ".join(parts)

    @staticmethod
    def recommend(prob: float, prediction: str) -> str:
        raise NotImplementedError


class URLDetector(_BaseDetector):
    """Phishing (positive) vs legitimate (negative) URL classifier."""

    labels = ("legitimate", "phishing")

    # Positive weight = makes the URL MORE risky when the feature is larger.
    feature_names = [
        "use_https", "has_ip_address", "has_at_symbol", "host_length",
        "num_dots", "num_subdomains", "is_suspicious_tld", "is_shortener",
        "is_cloud_host", "url_length", "path_length", "path_has_double_slash",
        "num_special_chars", "total_digits", "keyword_volume",
        "num_query_params", "has_redirect_param",
    ]
    # Negative weight for use_https (HTTPS lowers risk); positive for the rest.
    weights = [
        -1.8, 1.9, 2.0, 0.2, 0.35, 0.3, 1.2, 1.5, 0.4, 0.5, 0.35,
        0.6, 0.55, 0.25, 0.9, 0.4, 1.0,
    ]

    def features_from(self, raw: str) -> dict[str, float]:
        return extract_url_features(raw)

    @staticmethod
    def recommend(prob: float, prediction: str) -> str:
        if prediction == "phishing":
            return ("Do NOT click this link. It shows multiple phishing indicators. "
                    "Verify the real domain in your browser address bar and report it "
                    "to your security team / provider.")
        return ("Looks low-risk, but always hover to preview the real destination "
                "before entering sensitive data.")

    def _explain(self, top, feats, prob):
        base = super()._explain(top, feats, prob)
        if feats.get("use_https", 0) < 0.5:
            base += " The page is NOT served over HTTPS, so traffic is not encrypted."
        if feats.get("has_ip_address", 0) >= 0.5:
            base += " The URL points at a raw IP address instead of a real domain."
        return base


class EmailDetector(_BaseDetector):
    """Spam (positive) vs ham (negative) email / SMS classifier."""

    labels = ("ham", "spam")
    feature_names = ["word_count", "char_count", "has_urgent_words", "has_spoofed_provider",
                     "num_exclamations", "all_caps_ratio", "num_links", "contains_money",
                     "num_numbers", "length"]
    weights = [0.2, 0.1, 1.6, 1.3, 0.9, 0.9, 1.2, 1.0, 0.3, 0.2]

    def features_from(self, raw: str) -> dict[str, float]:
        text = raw.strip()
        words = re.findall(r"\b\w+\b", text.lower())
        caps = re.findall(r"[A-Z]", text)
        money = bool(re.search(r"(?:\$|€|£|\d+%|\bwin\b)", text, re.IGNORECASE))

        def ratio(v):  # cap to 1.5 to normalise
            return min(v, 1.5)

        return {
            "word_count": ratio(len(words) / 40.0),
            "char_count": ratio(len(text) / 200.0),
            "has_urgent_words": ratio(len([w for w in words if w in _URGENT_WORDS]) / 3.0),
            "has_spoofed_provider": ratio(len([p for p in _SPOOF_PROVIDERS if p in text.lower()]) / 3.0),
            "num_exclamations": ratio(text.count("!") / 4.0),
            "all_caps_ratio": ratio((len(caps) / max(len(text), 1)) * 10.0),
            "num_links": ratio(text.count("http") / 3.0),
            "contains_money": float(money),
            "num_numbers": ratio(len(re.findall(r"\d", text)) / 15.0),
            "length": ratio(len(text) / 300.0),
        }

    def predict_proba(self, raw):
        feats, prob = super().predict_proba(raw)
        return feats, prob

    @staticmethod
    def recommend(prob: float, prediction: str) -> str:
        if prediction == "spam":
            return ("Do not reply, click links, or provide information. Mark as Spam / "
                    "report phishing, and add the sender to your block list.")
        return "This message looks benign, but never share passwords via email."


class CredentialAnalyzer(_BaseDetector):
    """Password / credential risk scorer (weak=positive risk)."""

    labels = ("strong", "weak")
    feature_names = ["length", "has_upper", "has_lower", "has_digit", "has_symbol",
                   "entropy", "is_sequential", "has_repeats", "is_common"]
    # A positive baseline `intercept` means "risk by default"; strong
    # password traits (negative weights) subtract risk, while weak traits
    # (is_common / sequential / repeats) push the score back up.
    intercept = 0.8
    weights = [-1.5, -1.2, -0.5, -1.1, -1.3, -2.0, 2.5, 2.0, 3.0]

    COMMON = {"password", "123456", "123456789", "qwerty", "admin", "welcome",
              "letmein", "monkey", "12345", "111111", "dragon", "abc123",
              "password123", "iloveyou", "football", "admin123", "welcome1",
              "password1", "12345678", "qwerty123", "letmein1", "sunshine", "qwerty123"}
    COMMON_BASES = ("password", "admin", "welcome", "qwerty", "letmein",
                    "iloveyou", "dragon", "football", "monkey", "sunshine")
    SEQUENCES = ["1234", "5678", "abcd", "qwer", "asdf", "zxcv", "qwerty"]

    def features_from(self, raw: str) -> dict[str, float]:
        p = raw
        low = p.lower()
        caps = ''.join(c for c in p if c.isupper())
        lowers = ''.join(c for c in p if c.islower())
        digs = ''.join(c for c in p if c.isdigit())
        syms = ''.join(c for c in p if not c.isalnum())

        def shannon_entropy(s: str) -> float:
            if not s:
                return 0.0
            probs = [s.count(c) / len(s) for c in set(s)]
            return -sum(pr * math.log2(pr) for pr in probs)

        entropy = shannon_entropy(p)
        common_base = any(b in low for b in self.COMMON_BASES)
        # common if it's in the list, or a base word padded with digits
        is_common = (low in self.COMMON) or (common_base and bool(digs) and len(p) - len(syms) <= len(digs))
        # cap length/entropy so the model stays well-scaled
        return {
            "length": min(len(p) / 16.0, 2.0),
            "has_upper": min(len(caps) / 2.0, 1.0),
            "has_lower": min(len(lowers) / 2.0, 1.0),
            "has_digit": min(len(digs) / 2.0, 1.0),
            "has_symbol": min(len(syms) / 2.0, 1.0),
            "entropy": min(entropy / 60.0, 2.0),
            "is_sequential": float(any(seq in low for seq in self.SEQUENCES)),
            "has_repeats": float(len(set(p)) < max(len(p) * 0.5, 1)),
            "is_common": float(is_common),
        }

    def analyze_password(self, raw: str) -> dict[str, Any]:
        result = self.analyze(raw)
        result["entropy_bits"] = round(_shannon(raw), 1)
        return result

    @staticmethod
    def recommend(prob: float, prediction: str) -> str:
        if prediction == "weak":
            return ("Use a passphrase of 12+ characters mixing upper/lowercase, digits "
                    "and symbols. Enable Multi-Factor Authentication and use a password "
                    "manager with unique passwords per account.")
        return "Your password is strong. Keep it unique and enable MFA for extra safety."



def _shannon(s: str) -> float:
    if not s:
        return 0.0
    from collections import Counter
    c = Counter(s)
    return -sum((n / len(s)) * math.log2(n / len(s)) for n in c.values())