import uuid

from app.api.utils import get_user_store, get_post_store, get_place_store
from stores.place_store import PlaceStore
from stores.post_store import PostStore
from stores.user_store import UserStore
from fastapi import APIRouter, Depends, HTTPException

import schemas
from app.api import utils
from app.controllers.firebase import FirebaseUser, get_firebase_user

router = APIRouter()


@router.get("/{place_id}/icon", response_model=schemas.place.MapPinIcon)
def get_place_icon(
    place_id: uuid.UUID,
    firebase_user: FirebaseUser = Depends(get_firebase_user),
    user_store: UserStore = Depends(get_user_store),
    place_store: PlaceStore = Depends(get_place_store)
):
    user: schemas.internal.InternalUser = utils.get_user_from_uid_or_raise(user_store, firebase_user.uid)
    return place_store.get_place_icon(user.id, place_id)


@router.get("/{place_id}/mutualPosts", response_model=list[schemas.post.Post])
def get_mutual_posts(
    place_id: uuid.UUID,
    firebase_user: FirebaseUser = Depends(get_firebase_user),
    user_store: UserStore = Depends(get_user_store),
    post_store: PostStore = Depends(get_post_store)
):
    user: schemas.internal.InternalUser = utils.get_user_from_uid_or_raise(user_store, firebase_user.uid)
    mutual_posts = post_store.get_mutual_posts(user.id, place_id)
    if mutual_posts is None:
        raise HTTPException(404)
    return mutual_posts
