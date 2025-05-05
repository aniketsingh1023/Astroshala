# rag/settings.py
import os

# Define folder structure
BASE_DIR = "D:/HP Shared/All Freelance Projects/Astroved/astroved-backend"
PDF_DIR = PDF_DIR="D:/HP Shared/All Freelance Projects/Astroved/astroved-backend/pdf_files"
DB_DIR = os.path.join(BASE_DIR, "pdf_files/db")
CONFIG_PATH = os.path.join(BASE_DIR, "pdf_files/config.json")

# Ensure directories exist
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)