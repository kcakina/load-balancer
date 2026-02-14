import time
import threading

class RateStatus:
    def __init__(self, allowed: bool, remaining: int, reset_in_seconds: int):
        self.allowed = allowed
        self.remaining = remaining
        self.reset_in_seconds = reset_in_seconds

class Value:
    def __init__(self, start_ts: float, count: int):
        self.start_ts = start_ts
        self.count = count


class DB:
    def __init__(self):
        self.state = {}
        self.lock = threading.Lock()

    def validate_input(self, key: str, limit: int, window_seconds: int) -> bool:
        if not key or not limit > 0 or not window_seconds > 0:
            return False
        return True

    def check(self, key: str, limit: int, window_seconds: int) -> RateStatus:
        with self.lock:
            now = self.get_ts()
            state_key = (key, limit, window_seconds)

            # Step 2: Lookup — create if missing
            if state_key not in self.state:
                self.state[state_key] = Value(start_ts=now, count=0)

            value = self.state[state_key]

            # Step 3: Window reset
            if now - value.start_ts >= window_seconds:
                value.start_ts = now
                value.count = 0

            # Step 4: Decision
            if value.count < limit:
                value.count += 1
                allowed = True
            else:
                allowed = False

            # Step 5: Compute response fields
            reset_in_seconds = max(0, int(window_seconds - (now - value.start_ts)))
            remaining = max(0, limit - value.count) if allowed else 0

            return RateStatus(allowed=allowed, remaining=remaining, reset_in_seconds=reset_in_seconds)

    def get_ts(self) -> float:
        return time.time()