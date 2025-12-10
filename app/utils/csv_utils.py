import csv
import os
from typing import List
import time
from app.models.request_models import VisitRecord

UPLOAD_DIR = "uploads"

def ensure_upload_local_directory():
    """Ensure folder for local file creation is present"""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)


def generate_csv_file(records: List[VisitRecord]) -> str:
    """Generate CSV file locally and return file path."""
    ensure_upload_local_directory()

    timestamp = int(time.time() * 1000)
    filename = f"patient_intake_{timestamp}.csv"  # use timestamp for unique filename
    filepath = os.path.join(UPLOAD_DIR, filename)

    columns = [
        "mrn",
        "first_name",
        "last_name",
        "birth_date",
        "visit_account_number",
        "visit_date",
        "reason"
    ]

    with open(filepath, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()

        for record in records:
            writer.writerow(record.model_dump())

    return filepath, filename


def parse_csv(local_path):
    with open(local_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row