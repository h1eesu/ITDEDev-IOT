import configparser
from pathlib import Path

# Đường dẫn đến thư mục gốc của dự án
BASE_DIR = Path(__file__).resolve().parent

# Đọc file config.ini
config = configparser.ConfigParser()
config.read(BASE_DIR / "config.ini", encoding="utf-8")

# --- IP Webcam ---
IP_WEBCAM_URL = config.get("ip_webcam", "ip_webcam_url")

# --- Database ---
DB_PATH = BASE_DIR / config.get("database", "db_path")
DB_NAME = config.get("database", "db_name")

# --- Schema ---
SCHEMA_PATH = BASE_DIR / config.get("schema", "schema_path")

# --- Embeddings ---
EMBEDDINGS_NPY_PATH = BASE_DIR / config.get("embeddings", "embeddings_npy_path")

# --- Logging ---
LOG_PATH = BASE_DIR / config.get("logging", "log_path")

# --- Google Sheets ---
SHEET_KEY = BASE_DIR / config.get("google_sheet", "sheet_key")
SHEET_URL = config.get("google_sheet", "sheet_url")
