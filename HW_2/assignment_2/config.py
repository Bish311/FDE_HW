from pathlib import Path

BASE_DIR: Path = Path(__file__).resolve().parent
DB_PATH: Path = BASE_DIR / "database" / "flasheats.db"
DATA_DIR: Path = BASE_DIR / "data"
API_CACHE_DIR: Path = DATA_DIR / "raw_dispatch"

OUTPUT_DIR: Path = BASE_DIR / "output"
VALIDATION_DIR: Path = OUTPUT_DIR / "validation"
METRICS_DIR: Path = OUTPUT_DIR / "metrics"
MARTS_DIR: Path = OUTPUT_DIR / "marts"
AUDIT_DIR: Path = OUTPUT_DIR / "audit"
DOCS_DIR: Path = BASE_DIR / "docs"

API_BASE_URL: str = "http://127.0.0.1:8000"
API_ENDPOINT: str = f"{API_BASE_URL}/dispatch/orders"
API_PAGE_SIZE: int = 50
API_MAX_PAGES: int = 32
API_EXPECTED_TOTAL: int = 1600

SLA_LATE_THRESHOLD_MIN: float = 10.0
SEVERE_DELAY_THRESHOLD_MIN: float = 20.0
LEADERSHIP_THRESHOLD_MIN: float = 0.0

ENGINEER_PERSONA: str = "BISHWAYAN CHATTERJEE -- 10200"
