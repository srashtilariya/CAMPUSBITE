"""HTTP layer. ``api_router`` bundles every feature router under the /api prefix."""
from fastapi import APIRouter

from app.api import accounts, catalog, couriers, customer_orders, insights, kitchen

api_router = APIRouter(prefix="/api")
for feature in (accounts, catalog, customer_orders, kitchen, couriers, insights):
    api_router.include_router(feature.router)
