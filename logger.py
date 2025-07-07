import csv
import os
import cv2
import re

LOG_FILE = "data/visitor_log.csv"

# ✅ Ensure log file exists with correct headers
def init_log():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Plate", "Name", "Flat", "Purpose", "Status", "Direction", "EntryTime", "ExitTime", "Intrusion"])

# ✅ Save a new entry with snapshot
def log_entry(info, timestamp, direction, frame, intrusion=False):
    init_log()
    img_path = f"snapshots/{info['plate']}_{timestamp.replace(':', '-')}.jpg"
    if not os.path.exists("snapshots"):
        os.makedirs("snapshots")
    cv2.imwrite(img_path, frame)

    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            info['plate'],
            info.get('name', "Unknown"),
            info.get('flat', "Unknown"),
            info.get('purpose', "Unknown"),
            info.get('status', "Pending"),
            direction,
            timestamp,
            "",  # ExitTime
            "Yes" if intrusion else "No"
        ])

# ✅ Update exit timestamp when a vehicle leaves
def update_exit(plate, exit_time):
    init_log()
    rows = []
    with open(LOG_FILE, mode='r') as file:
        rows = list(csv.reader(file))

    for i in range(len(rows) - 1, 0, -1):
        if rows[i][0] == plate and rows[i][7] == "":
            rows[i][7] = exit_time
            break

    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

# ✅ Get last approval status for a plate
def load_latest_status(plate):
    init_log()
    with open(LOG_FILE, mode='r') as file:
        rows = list(csv.reader(file))
        for row in reversed(rows):
            if row[0] == plate:
                return row[4]  # Status
    return "Unknown"

# ✅ Extract the most likely plate number using regex + confidence
def extract_likely_plate(results):
    plate_pattern = r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{3,4}$'
    for _, text, conf in results:
        cleaned = text.replace(" ", "").upper()
        if re.match(plate_pattern, cleaned) and conf > 0.5:
            return cleaned
    return None


def check_previous_entry(plate):
    init_log()
    with open(LOG_FILE, mode='r') as file:
        rows = list(csv.reader(file))
        for row in reversed(rows):
            if row[0] == plate:
                return row[4]  # Status column
    return "Unknown"
