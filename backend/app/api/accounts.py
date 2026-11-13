"""Sign-up, sign-in and "who am I"."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth_guards import current_account
from app.core.db import db_session
from app.core.passwords import check_password, make_hash
from app.core.tokens import issue_token
from app.models import Account, Restaurant, Role
from app.schemas.accounts import AccountView, Credentials, SessionGrant, SignupForm

router = APIRouter(prefix="/auth", tags=["Auth"])


def _grant(account: Account) -> SessionGrant:
    return SessionGrant(
        access_token=issue_token(account.id, account.role.value),
        user=AccountView.model_validate(account),
    )


def _find_by_email(db: Session, email: str) -> Account | None:
    return db.query(Account).filter(Account.email == email.lower()).first()


@router.post("/register", response_model=SessionGrant, status_code=status.HTTP_201_CREATED)
def sign_up(form: SignupForm, db: Session = Depends(db_session)):
    if _find_by_email(db, form.email) is not None:
        raise HTTPException(status_code=409, detail="Email is already registered")

    account = Account(
        name=form.name.strip(),
        email=form.email.lower(),
        password_hash=make_hash(form.password),
        role=form.role,
        phone=form.phone,
        address=form.address,
    )
    db.add(account)

    if account.role is Role.RESTAURANT_OWNER:
        # Every owner gets a restaurant straight away so the dashboard isn't empty.
        kitchen_name = form.restaurant_name or f"{account.name}'s Kitchen"
        db.add(Restaurant(owner=account, name=kitchen_name.strip(), address=form.address))

    db.commit()
    db.refresh(account)
    return _grant(account)


@router.post("/login", response_model=SessionGrant)
def sign_in(creds: Credentials, db: Session = Depends(db_session)):
    account = _find_by_email(db, creds.email)
    if account is None or not check_password(creds.password, account.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return _grant(account)


@router.get("/me", response_model=AccountView)
def whoami(account: Account = Depends(current_account)):
    return account
