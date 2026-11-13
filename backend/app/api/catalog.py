"""Public browsing: restaurants, their menus and their reviews. No login needed."""
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.db import db_session
from app.domain.listing import page_of
from app.domain.presenters import present_review
from app.models import MenuEntry, Restaurant, Review
from app.schemas.catalog import DishView, RestaurantCard, ReviewView
from app.schemas.common import Paginated

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])

MENU_ORDERINGS = {
    "name": MenuEntry.name,
    "price_asc": MenuEntry.price.asc(),
    "price_desc": MenuEntry.price.desc(),
}


def _ratings(db: Session, restaurant_ids: list[int]) -> dict[int, tuple[float, int]]:
    """restaurant id -> (average rating rounded to 2dp, review count), for those with reviews."""
    if not restaurant_ids:
        return {}
    rows = (
        db.query(Review.restaurant_id, func.avg(Review.rating), func.count(Review.id))
        .filter(Review.restaurant_id.in_(restaurant_ids))
        .group_by(Review.restaurant_id)
    )
    return {rid: (round(float(mean), 2), n) for rid, mean, n in rows}


def _card(restaurant: Restaurant, ratings: dict[int, tuple[float, int]]) -> RestaurantCard:
    card = RestaurantCard.model_validate(restaurant)
    if restaurant.id not in ratings:
        return card
    mean, count = ratings[restaurant.id]
    return card.model_copy(update={"avg_rating": mean, "review_count": count})


def _restaurant_or_404(db: Session, restaurant_id: int) -> Restaurant:
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@router.get("", response_model=Paginated[RestaurantCard])
def browse_restaurants(
    search: str | None = None,
    cuisine: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    db: Session = Depends(db_session),
):
    query = db.query(Restaurant)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(or_(Restaurant.name.ilike(pattern), Restaurant.cuisine.ilike(pattern)))
    if cuisine:
        query = query.filter(Restaurant.cuisine.ilike(cuisine))

    listing = page_of(query.order_by(Restaurant.name), page, page_size)
    ratings = _ratings(db, [r.id for r in listing["items"]])
    listing["items"] = [_card(r, ratings) for r in listing["items"]]
    return listing


@router.get("/{restaurant_id}", response_model=RestaurantCard)
def restaurant_profile(restaurant_id: int, db: Session = Depends(db_session)):
    restaurant = _restaurant_or_404(db, restaurant_id)
    return _card(restaurant, _ratings(db, [restaurant.id]))


@router.get("/{restaurant_id}/menu", response_model=Paginated[DishView])
def restaurant_menu(
    restaurant_id: int,
    search: str | None = None,
    category: str | None = None,
    min_price: Decimal | None = Query(None, ge=0),
    max_price: Decimal | None = Query(None, ge=0),
    available_only: bool = False,
    sort: str = Query("name", pattern="^(name|price_asc|price_desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(db_session),
):
    _restaurant_or_404(db, restaurant_id)
    price_bounds_given = min_price is not None and max_price is not None
    if price_bounds_given and min_price > max_price:
        raise HTTPException(status_code=400, detail="min_price cannot exceed max_price")

    conditions = [MenuEntry.restaurant_id == restaurant_id, MenuEntry.is_deleted.is_(False)]
    if search:
        conditions.append(MenuEntry.name.ilike(f"%{search.strip()}%"))
    if category:
        conditions.append(MenuEntry.category.ilike(category))
    if min_price is not None:
        conditions.append(MenuEntry.price >= min_price)
    if max_price is not None:
        conditions.append(MenuEntry.price <= max_price)
    if available_only:
        conditions.append(MenuEntry.is_available.is_(True))

    query = db.query(MenuEntry).filter(*conditions).order_by(MENU_ORDERINGS[sort])
    return page_of(query, page, page_size)


@router.get("/{restaurant_id}/reviews", response_model=Paginated[ReviewView])
def restaurant_reviews(
    restaurant_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(db_session),
):
    query = db.query(Review).filter(Review.restaurant_id == restaurant_id).order_by(Review.created_at.desc())
    return page_of(query, page, page_size, present_review)
