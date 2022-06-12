from fastapi import APIRouter

api_router = APIRouter(
    prefix="/api",
    tags=["api"]
)


from . import docs
api_router.include_router(docs.router)

from . import analysis_results
api_router.include_router(analysis_results.router)

from . import sources
api_router.include_router(sources.router)

from . import blacklisted_sources
api_router.include_router(blacklisted_sources.router)