C1: Tested duration_minutes:
    ("09:00", "10:30") -> 90
    ("23:30", "00:45") -> 75   (crosses midnight, handled by +24h)
    ("00:00", "00:00") -> 0
Durations are non-negative in all tested cases.
