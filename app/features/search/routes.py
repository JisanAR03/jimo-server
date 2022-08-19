from fastapi import APIRouter, Depends

from app.features.search.search_store import SearchStore
from app.features.users.dependencies import get_caller_user, JimoUser
from app.features.users.entities import PublicUser
from app.features.stores import get_search_store

router = APIRouter()


@router.get("/users", response_model=list[PublicUser])
async def search_users(
    q: str,
    search_store: SearchStore = Depends(get_search_store),
    _wrapped_user: JimoUser = Depends(get_caller_user),
):
    """Search for users with the given query."""
    return await search_store.search_users(keyword=q)
