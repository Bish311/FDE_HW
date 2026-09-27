import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any
from pipeline.models import OrderRecord

logger = logging.getLogger("pipeline.ingest_db")

def fetch_sqlite_orders(db_path: Path) -> List[OrderRecord]:
    connection: sqlite3.Connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    cursor: sqlite3.Cursor = connection.cursor()
    cursor.execute("SELECT * FROM orders")
    rows: List[sqlite3.Row] = cursor.fetchall()
    orders: List[OrderRecord] = []
    for row in rows:
        order_dict: Dict[str, Any] = dict(row)
        order_record: OrderRecord = {
            "order_id": str(order_dict["order_id"]),
            "customer_id": str(order_dict["customer_id"]),
            "restaurant_id": str(order_dict["restaurant_id"]),
            "driver_id": str(order_dict["driver_id"]),
            "city": str(order_dict["city"]),
            "created_at": str(order_dict["created_at"]),
            "promised_eta": str(order_dict["promised_eta"]),
            "pickup_at": order_dict["pickup_at"],
            "actual_delivery_at": order_dict["actual_delivery_at"],
            "final_status": str(order_dict["final_status"]),
            "distance_km_estimate": float(order_dict["distance_km_estimate"] or 0.0),
            "traffic_bucket": str(order_dict["traffic_bucket"]),
            "weather_bucket": str(order_dict["weather_bucket"]),
        }
        orders.append(order_record)
    connection.close()
    logger.info("Extracted %d orders from SQLite", len(orders))
    return orders

def fetch_sqlite_table(db_path: Path, table_name: str) -> List[Dict[str, Any]]:
    connection: sqlite3.Connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    cursor: sqlite3.Cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows: List[sqlite3.Row] = cursor.fetchall()
    results: List[Dict[str, Any]] = []
    for row in rows:
        results.append(dict(row))
    connection.close()
    logger.info("Extracted %d rows from table %s", len(results), table_name)
    return results
