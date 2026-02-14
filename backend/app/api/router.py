"""
CodeGenie AI Editor — Central API Router
Mounts all v1 sub-routers under /api/v1.
"""

from fastapi import APIRouter

from app.api.v1 import api_keys, chat, completion, explain
from app.api.v1 import indexing, bug_detection, refactor, test_generation
from app.api.v1 import git
from app.api.v1 import search
from app.api.v1 import agent, multi_refactor

# Main API router
api_router = APIRouter(prefix="/api/v1")

# Mount sub-routers
api_router.include_router(api_keys.router)
api_router.include_router(chat.router)
api_router.include_router(completion.router)
api_router.include_router(explain.router)
api_router.include_router(indexing.router)
api_router.include_router(bug_detection.router)
api_router.include_router(refactor.router)
api_router.include_router(test_generation.router)
api_router.include_router(git.router)
api_router.include_router(search.router)
api_router.include_router(agent.router)
api_router.include_router(multi_refactor.router)

