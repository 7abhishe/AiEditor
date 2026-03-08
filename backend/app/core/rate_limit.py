"""
CodeGenie AI Editor — Rate Limiting Configuration
Uses slowapi to prevent brute-force attacks, signup spam, and AI endpoint abuse.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Global limiter instance — keyed by client IP
limiter = Limiter(key_func=get_remote_address)
