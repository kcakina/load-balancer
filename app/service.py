from app.db import DB, RateStatus
from typing import Optional

class LimiterInput:
    def __init__(self, key: str, limit: int, window_seconds: int):
        self.key = key
        self.limit = limit
        self.window_seconds = window_seconds


def run_rate_check(db: DB, input: LimiterInput ) -> Optional[RateStatus] :
    if db.validate_input(input.key, input.limit, input.window_seconds):
        return db.check(input.key, input.limit, input.window_seconds)
    else:
        return None



