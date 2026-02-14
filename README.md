IN-MEMORY RATE LIMITER (FIXED WINDOW) — SINGLE CHALLENGE SPEC

Goal:
Implement a fixed-window rate limiter with one endpoint:

POST /check

--------------------------------------------------
REQUEST
--------------------------------------------------
JSON body:
{
  "key": "string",
  "limit": 5,
  "window_seconds": 10
}

--------------------------------------------------
RESPONSE
--------------------------------------------------
JSON:
{
  "allowed": true,
  "remaining": 4,
  "reset_in_seconds": 9
}

Definitions:
- key: client identifier
- limit: max requests allowed per window
- window_seconds: window size in seconds
- Each /check call represents ONE attempted request.
- If allowed=true, the request counts toward the quota.

--------------------------------------------------
CORE BEHAVIOR (FIXED WINDOW)
--------------------------------------------------
Use an in-memory dict:

state[(key, limit, window_seconds)] = {
    "start_ts": float,
    "count": int
}

Algorithm for each check at time now:

1) Validate input:
   - key must exist and not be empty
   - limit must be int > 0
   - window_seconds must be int > 0
   - otherwise return HTTP 400

2) Lookup entry in state.
   - If missing:
       create {start_ts = now, count = 0}

3) Window reset:
   - If now - start_ts >= window_seconds:
       reset to {start_ts = now, count = 0}

4) Decision:
   - If count < limit:
       count += 1
       allowed = true
   - Else:
       allowed = false

5) Compute response fields:
   reset_in_seconds =
       max(0, int(window_seconds - (now - start_ts)))

   remaining =
       if allowed:
           max(0, limit - count)   # AFTER increment
       else:
           0

6) Return JSON response.

--------------------------------------------------
CONCURRENCY REQUIREMENT
--------------------------------------------------
Use a single global threading.Lock().
Wrap read/update logic so two concurrent requests
cannot both increment past the limit.

--------------------------------------------------
MEMORY RULE
--------------------------------------------------
No background cleanup needed.
Lazy reset on access is sufficient.

--------------------------------------------------
TEST CASES (REQUIRED)
--------------------------------------------------
Assume limit=2, window=10:

1) t=0:
   check -> allowed (remaining=1)
   check -> allowed (remaining=0)
   check -> blocked (remaining=0)

2) t=10 or later:
   check -> allowed again

3) Different keys are isolated.

4) Same key with different limit/window
   should be tracked independently.

--------------------------------------------------
DELIVERABLES
--------------------------------------------------
- RateLimiter class with method:
      check(key, limit, window_seconds)

- Flask endpoint:
      POST /check
  which calls the limiter and returns JSON.
