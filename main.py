import time
import cv2
from detection import setup_video_source, process_frame
from ui_security import get_visitor_details
from logger import log_entry, check_previous_entry
from notifier import request_approval, get_approval_status

print("[SYSTEM] Smart Gate System Started")

VIDEO_SOURCE = "sample-video.mp4"  # Change to 0 if using webcam
cap = setup_video_source(VIDEO_SOURCE)

no_detection_count = 0
MAX_NO_DETECTION = 1000
frame_count = 0
MAX_FRAMES = 500  # For testing, stop after 500 frames

try:
    while True:
        frame_count += 1
        if frame_count > MAX_FRAMES:
            print("[INFO] Max frame count reached. Exiting.")
            break

        result = process_frame(cap)

        if result == "END":
            break

        if result:
            no_detection_count = 0
            plate_number = result['plate']
            snapshot = result['snapshot']
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

            print(f"[DETECTED] Plate: {plate_number}")

            last_status = check_previous_entry(plate_number)

            if last_status == 'Denied':
                print(f"[ALERT] Intrusion detected! Plate: {plate_number}")
                log_entry({'plate': plate_number}, timestamp, "entry", snapshot, intrusion=True)
                continue

            visitor_info = get_visitor_details(plate_number)
            visitor_info['plate'] = plate_number
            visitor_info['timestamp'] = timestamp

            request_approval(visitor_info)
            decision = get_approval_status(visitor_info['flat'])

            visitor_info['status'] = decision
            log_entry(visitor_info, timestamp, "entry", snapshot)

            try:
                cv2.imshow("Smart Gate - Frame", result['snapshot'])
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            except Exception as e:
                print(f"[ERROR] Display error: {e}")

        else:
            no_detection_count += 1
            if no_detection_count > MAX_NO_DETECTION:
                print("[INFO] Too many frames without detection. Exiting.")
                break

except KeyboardInterrupt:
    print("\n[INFO] Interrupted by user.")

finally:
    cap.release()
    try:
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"[ERROR] cv2.destroyAllWindows() failed: {e}")