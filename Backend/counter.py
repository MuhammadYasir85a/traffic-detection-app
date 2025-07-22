import cv2
import numpy as np
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import time

# Load YOLOv8 model (you can use yolov8n.pt or your trained model)
model = YOLO("yolov8n.pt")

# Initialize Deep SORT tracker
tracker = DeepSort(max_age=30)

# Video input
cap = cv2.VideoCapture("sample.mp4")  # Replace with your video path or 0 for webcam

# Line coordinates for counting
line_y = 400
offset = 20  # To check near the line
counted_ids = set()
vehicle_count = 0

# Vehicle class names for YOLO COCO dataset indices
class_names = {2: 'Car', 3: 'Motorcycle', 7: 'Truck'}

# Colors for different vehicle types (BGR)
colors = {
    'Car': (0, 255, 0),          # Green
    'Motorcycle': (255, 165, 0), # Orange
    'Truck': (0, 140, 255)       # Dark Orange
}

# For count animation
count_animation_start = None
count_animation_duration = 0.5  # seconds

def draw_glowing_box(img, pt1, pt2, color, thickness=2, glow_radius=10):
    overlay = img.copy()
    alpha = 0.6
    # Draw glow by multiple rectangles with increasing thickness and decreasing alpha
    for i in range(glow_radius, 0, -2):
        glow_color = tuple(min(255, int(c * (alpha * (i / glow_radius)))) for c in color)
        cv2.rectangle(overlay, pt1, pt2, glow_color, thickness=i)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    # Draw main rectangle
    cv2.rectangle(img, pt1, pt2, color, thickness)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)[0]

    detections = []

    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        conf = float(box.conf[0])
        cls = int(box.cls[0])

        # Only count car (2), motorcycle (3), truck (7)
        if cls in [2, 3, 7] and conf > 0.3:
            detections.append(([x1, y1, x2 - x1, y2 - y1], conf, 'vehicle', cls))

    tracks = tracker.update_tracks(detections, frame=frame)

    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id
        ltrb = track.to_ltrb()
        x1, y1, x2, y2 = map(int, ltrb)

        # Calculate center of track box
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)

        # Find closest detection to this center
        min_dist = float('inf')
        vehicle_cls = None
        for det in detections:
            (dx, dy, dw, dh), conf, _, cls = det
            det_cx = int(dx + dw / 2)
            det_cy = int(dy + dh / 2)
            dist = (det_cx - center_x) ** 2 + (det_cy - center_y) ** 2
            if dist < min_dist:
                min_dist = dist
                vehicle_cls = cls

        vehicle_type = class_names.get(vehicle_cls, 'Unknown')
        color = colors.get(vehicle_type, (255, 255, 255))

        # Draw glowing bounding box
        draw_glowing_box(frame, (x1, y1), (x2, y2), color, thickness=2, glow_radius=12)

        # Draw ID and vehicle type label
        label = f'ID {track_id} {vehicle_type}'
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Count if center crosses the line and not already counted
        if line_y - offset < center_y < line_y + offset and track_id not in counted_ids:
            vehicle_count += 1
            counted_ids.add(track_id)
            count_animation_start = time.time()

    # Draw the counting line
    cv2.line(frame, (0, line_y), (frame.shape[1], line_y), (0, 0, 255), 2)

    # Animate count display
    if count_animation_start:
        elapsed = time.time() - count_animation_start
        if elapsed < count_animation_duration:
            scale = 1 + 0.5 * (1 - elapsed / count_animation_duration)
            thickness = int(3 * scale)
            font_scale = 1.2 * scale
            color = (0, 0, 255)
        else:
            scale = 1
            thickness = 3
            font_scale = 1.2
            color = (0, 0, 255)
            count_animation_start = None
    else:
        scale = 1
        thickness = 3
        font_scale = 1.2
        color = (0, 0, 255)

    cv2.putText(frame, f'Count: {vehicle_count}', (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

    cv2.imshow("Vehicle Counter", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
