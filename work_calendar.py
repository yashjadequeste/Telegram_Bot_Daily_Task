import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

# true = bot + scheduler work Sat/Sun too (for testing only)
ALLOW_WEEKEND_TEST = os.getenv("ALLOW_WEEKEND_TEST", "false").lower() in (
    "1",
    "true",
    "yes",
    "on",
)


def is_working_day(dt=None):
    if ALLOW_WEEKEND_TEST:
        return True

    dt = dt or datetime.now()
    return dt.weekday() < 5
