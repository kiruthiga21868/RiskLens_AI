"""
Centralized logging configuration.

WHY THIS FILE EXISTS
    Consistent, structured logs are critical for debugging and for
    security audit trails (who did what, when). A single setup function
    means every module logs in the same format and can be re-leveled
    globally with one change.

BEST PRACTICE
    - Log to stdout (containers/Docker capture it automatically).
    - Include a timestamp + logger name so messages are traceable.
    - Keep uvicorn's access logs at WARNING to reduce noise in dev.
"""
import logging
import sys

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def setup_logging(level: int = logging.INFO) -> None:
    """Configure the root logger once, applied application-wide."""
    handlers = [logging.StreamHandler(sys.stdout)]

    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=handlers,
    )

    # Reduce noise from uvicorn's per-request access logs during dev
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
