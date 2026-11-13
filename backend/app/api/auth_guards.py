"""FastAPI dependencies for "who is calling, and are they allowed to?"."""
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.db import db_session
from app.core.tokens import read_token
from app.models import Account, Restaurant, Role

_bearer = HTTPBearer(auto_error=False)


def _not_authenticated() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def current_account(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(db_session),
) -> Account:
    claims = read_token(creds.credentials) if creds else None
    subject = claims.get("sub") if claims else None
    account = db.get(Account, int(subject)) if subject else None
    if account is None:
        raise _not_authenticated()
    return account


def roles_allowed(*roles: Role) -> Callable[..., Account]:
    """Build a dependency that only lets the given roles through (403 for everyone else)."""
    allowed = frozenset(roles)

    def guard(account: Account = Depends(current_account)) -> Account:
        if account.role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return account

    return guard


customer_only = roles_allowed(Role.CUSTOMER)
owner_only = roles_allowed(Role.RESTAURANT_OWNER)
courier_only = roles_allowed(Role.DELIVERY_PARTNER)


def owned_restaurant(owner: Account = Depends(owner_only), db: Session = Depends(db_session)) -> Restaurant:
    restaurant = db.query(Restaurant).filter_by(owner_id=owner.id).first()
    if restaurant is None:
        raise HTTPException(status_code=404, detail="No restaurant linked to this owner")
    return restaurant
