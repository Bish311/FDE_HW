import logging
from typing import List, Dict, Any

logger = logging.getLogger("pipeline.transform_dims")

def build_dim_customers(raw_rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    lookup: Dict[str, Dict[str, Any]] = {}
    for row in raw_rows:
        cid: str = str(row["customer_id"])
        lookup[cid] = {
            "customer_id": cid,
            "name": str(row["name"]),
            "email": str(row["email"]),
            "lat": float(row["lat"] or 0.0),
            "lon": float(row["lon"] or 0.0),
        }
    logger.info("Built dim_customers with %d entities", len(lookup))
    return lookup

def build_dim_restaurants(raw_rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    lookup: Dict[str, Dict[str, Any]] = {}
    for row in raw_rows:
        rid: str = str(row["restaurant_id"])
        lookup[rid] = {
            "restaurant_id": rid,
            "restaurant_name": str(row["restaurant_name"]),
            "cuisine": str(row["cuisine"]),
            "lat": float(row["lat"] or 0.0),
            "lon": float(row["lon"] or 0.0),
        }
    logger.info("Built dim_restaurants with %d entities", len(lookup))
    return lookup

def build_dim_drivers(raw_rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    lookup: Dict[str, Dict[str, Any]] = {}
    for row in raw_rows:
        did: str = str(row["driver_id"])
        lookup[did] = {
            "driver_id": did,
            "rating": float(row["rating"] or 0.0),
            "vehicle_type": str(row["vehicle_type"]),
            "experience_months": int(row["experience_months"] or 0),
        }
    logger.info("Built dim_drivers with %d entities", len(lookup))
    return lookup
