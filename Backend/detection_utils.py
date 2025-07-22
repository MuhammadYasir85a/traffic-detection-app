# detection_utils.py
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import cv2

model = YOLO("yolov8n.pt")
tracker = DeepSort(max_age=30)
class_names = {2: 'Car', 3: 'Motorcycle', 7: 'Truck'}

def detect_vehicles(frame):
    results = model(frame)[0]
    detections = []

    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        if cls in class_names and conf > 0.3:
            detections.append(([x1, y1, x2 - x1, y2 - y1], conf, 'vehicle', cls))

    tracks = tracker.update_tracks(detections, frame=frame)
    vehicle_count = 0
    count_by_type = {'Car': 0, 'Truck': 0, 'Motorcycle': 0}

    for track in tracks:
        if not track.is_confirmed():
            continue
        ltrb = track.to_ltrb()
        x1, y1, x2, y2 = map(int, ltrb)
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)

        cls = detections[0][3] if detections else 2
        label = class_names.get(cls, "Vehicle")
        color = (0, 255, 0)
        count_by_type[label] += 1
        vehicle_count += 1

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    return frame, vehicle_count, count_by_type

def detect_vehicles_from_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    final_frame = None
    total_counts = {'Car': 0, 'Truck': 0, 'Motorcycle': 0}

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % 5 != 0:
            continue  # Process every 5th frame

        processed, _, counts = detect_vehicles(frame)
        final_frame = processed  # Use last processed frame as preview

        for k in total_counts:
            total_counts[k] += counts[k]

    cap.release()
    total_count = sum(total_counts.values())
    return final_frame, total_count, total_counts
