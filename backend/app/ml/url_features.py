"""
URL feature extraction - the heart of URL phishing detection.

WHY ENGINEERING FEATURES
    Raw URLs are strings; ML models need numbers. We encode the
    heuristics security analysts actually look for as numerical
    features. Each feature is also *interpretable*, which is exactly
    what SHAP needs to produce human-readable explanations.

    We keep feature values roughly comparable (many are capped / bounded)
    so a logistic-regression style model behaves like a clean weighted
    risk model and SHAP values are intuitive.
"""
import ipaddress
import re
from urllib.parse import parse_qs, urlparse

SHORTENER_DOMAINS = {"bit.ly", "tinyurl.com", "t.co", "cutt.ly", "is.gd",
                     "ow.ly", "goo.gl", "tiny.cc", "buff.ly"}
CLOUD_PROVIDERS = {"amazonaws.com", "azureedge.net", "cloudfront.net",
                   "firebaseapp.com", "vercel.app"}
SUSPICIOUS_TLDS = {".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top",
                   ".icu", ".bid", ".download"}
KEYWORDS = ("login", "signin", "verify", "secure", "account", "update",
            "win", "prize", "bank", "paypal", "password")


def _normalise(url: str) -> str:
    """Ensure the URL has a scheme so urlparse behaves predictably."""
    url = url.strip()
    if not url:
        raise ValueError("URL cannot be empty")
    if re.match(r"^[a-z][a-z0-9+.-]*://", url, re.IGNORECASE):
        return url
    return "http://" + url


def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host.strip("[]"))
        return True
    except ValueError:
        return False


def extract_url_features(url: str) -> dict[str, float]:
    """Extract an interpretable, numeric security feature vector from a URL."""
    parsed = urlparse(_normalise(url))
    host = (parsed.hostname or "").lower().rstrip(".")
    path = parsed.path or ""
    query = parse_qs(parsed.query)

    flag = lambda c: 1.0 if c else 0.0  # noqa: E731
    capped = lambda v, m: min(float(v) / m, 2.0)  # noqa: E731

    num_digits = sum(ch.isdigit() for ch in url)
    num_special = sum(1 for ch in url if ch in "!=;,%$*+")
    num_keywords = len(re.findall(r"(?i)(?:%s)" % "|".join(KEYWORDS), url))

    features = {
        # Transport & address
        "use_https": flag(parsed.scheme == "https"),
        "has_ip_address": flag(_is_ip(host)),
        "has_at_symbol": flag("@" in url),

        # Domain structure
        "host_length": capped(len(host), 30),
        "num_dots": capped(host.count("."), 4),
        "num_subdomains": capped(max(host.count(".") - 1, 0), 4),
        "is_suspicious_tld": flag(any(host.endswith(t) for t in SUSPICIOUS_TLDS)),
        "is_shortener": flag(any(host == d or host.endswith("." + d) for d in SHORTENER_DOMAINS)),
        "is_cloud_host": flag(any(host.endswith(c) for c in CLOUD_PROVIDERS)),

        # Path & size
        "url_length": capped(len(url), 100),
        "path_length": capped(len(path), 100),
        "path_has_double_slash": flag("//" in path),
        "path_has_tilda": flag("~" in path),
        "num_special_chars": capped(num_special, 5),
        "total_digits": capped(num_digits, 20),
        "keyword_volume": capped(num_keywords, 4),

        # Query indicators
        "num_query_params": capped(len(query), 5),
        "has_redirect_param": flag("url" in query or "redirect" in query),
    }

    return features