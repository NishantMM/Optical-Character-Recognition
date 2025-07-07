import cv2
import numpy as np
import easyocr
from ultralytics import YOLO
from logger import extract_likely_plate  # Your custom logic

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Initialize OCR reader
reader = easyocr.Reader(['en'])

ALLOWED_CLASSES = {'car', 'motorbike', 'bus', 'truck'}

def setup_video_source(source=0):
    return cv2.VideoCapture(source)

def process_frame(cap):
    ret, frame = cap.read()
    if not ret:
        print("[INFO] End of video or can't read frame.")
        return "END"

    results = model(frame)[0]  # Get predictions

    car_detected = False

    for box in results.boxes:
        class_id = int(box.cls[0])
        label = model.names[class_id]
        confidence = float(box.conf[0])

        print(f"[YOLO DEBUG] Class: {label} (Confidence: {confidence:.2f})")

        if label not in ALLOWED_CLASSES or confidence < 0.3:
            continue

        car_detected = True

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        car_crop = frame[y1:y2, x1:x2]

        if car_crop.size == 0 or car_crop.shape[0] < 30 or car_crop.shape[1] < 30:
            print("[WARN] Invalid crop size, skipping OCR.")
            continue

        try:
            result = reader.readtext(car_crop)
            print(f"[OCR RESULT] {result}")
        except Exception as e:
            print(f"[ERROR] OCR failed: {e}")
            continue

        plate = extract_likely_plate(result)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, plate if plate else "No plate", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        if plate:
            # No direction: just return plate and snapshot
            return {
                'plate': plate,
                'snapshot': frame.copy()
            }

    if not car_detected:
        print("[DEBUG] No car detected.")

    return None