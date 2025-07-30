# detection_utils.py
import torch
import cv2
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from collections import defaultdict
from ultralytics.nn.tasks import DetectionModel

torch.serialization.add_safe_globals([DetectionModel])
# Load YOLOv8 model
model = YOLO('yolov8n.pt')

# Initialize DeepSORT tracker
tracker = DeepSort(max_age=30)

# Class map for COCO
class_names = {
    2: "Car",
    3: "Motorcycle", 
    7: "Truck"
}

# Global variables for video processing
count_by_type_global = defaultdict(int)
counted_ids = set()
previous_centers = {}

# Red line configuration for video (if needed)
LINE_Y = 300
LINE_OFFSET = 10
line_thickness = 3

def get_class_color(cls_name):
    """Get color for each vehicle class"""
    colors = {
        "Car": (0, 255, 0),      # Green
        "Truck": (255, 0, 0),    # Blue  
        "Motorcycle": (0, 255, 255)  # Yellow
    }
    return colors.get(cls_name, (255, 255, 255))

def display_image_counts(frame, counts):
    """Display counts on static image"""
    
    
    
def detect_vehicles(frame):
    """
    Process static image - count all detected objects,
    addressing cases where a single object might be classified as multiple types.
    """
    results = model(frame, verbose=False)[0]
    
    # Initialize counts for this image
    count_by_type = {"Car": 0, "Truck": 0, "Motorcycle": 0}
    
    # Store detected boxes that are relevant
    valid_detections = [] 
    
    # Process each detection from YOLO results
    for box in results.boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        
        # Filter by confidence and relevant classes
        if conf > 0.4 and cls in class_names:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_name = class_names[cls]
            
            # Store detection details for later processing to avoid overlaps
            valid_detections.append({
                'bbox': (x1, y1, x2, y2),
                'confidence': conf,
                'class_id': cls,
                'class_name': cls_name
            })
    
    # Apply a custom Non-Maximum Suppression (NMS) across different classes
    # to handle cases where a single object gets multiple, overlapping classifications.
    
    final_counted_objects = []

    # Sort detections by confidence in descending order
    valid_detections.sort(key=lambda x: x['confidence'], reverse=True)

    for det1 in valid_detections:
        x1a, y1a, x2a, y2a = det1['bbox']
        is_duplicate = False
        
        for final_det in final_counted_objects:
            x1b, y1b, x2b, y2b = final_det['bbox']

            # Calculate Intersection over Union (IoU)
            xA = max(x1a, x1b)
            yA = max(y1a, y1b)
            xB = min(x2a, x2b)
            yB = min(y2a, y2b)

            inter_area = max(0, xB - xA + 1) * max(0, yB - yA + 1)
            boxAArea = (x2a - x1a + 1) * (y2a - y1a + 1)
            boxBArea = (x2b - x1b + 1) * (y2b - y1b + 1)
            
            # Avoid division by zero if both areas are zero (shouldn't happen with valid boxes)
            union_area = float(boxAArea + boxBArea - inter_area)
            iou = inter_area / union_area if union_area > 0 else 0

            # If IoU is above a threshold, consider them the same physical object.
            # This is where we prevent double counting across different classes for the same object.
            # Adjust this threshold (e.g., 0.2 to 0.5) based on how strictly you want to merge.
            # A value like 0.3-0.4 is a good starting point for merging highly overlapping boxes.
            if iou > 0.35: # Slightly adjusted threshold for robust merging
                is_duplicate = True
                break
        
        if not is_duplicate:
            final_counted_objects.append(det1)
            count_by_type[det1['class_name']] += 1
            
            # Draw bounding box and labels for the selected detection
            x1, y1, x2, y2 = det1['bbox']
            cls_name = det1['class_name']
            conf = det1['confidence']
            color = get_class_color(cls_name)
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw class name and confidence
            label = f'{cls_name}: {conf:.2f}'
            
            # Adjust text position to ensure visibility (move up if too close to top, or inside if needed)
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            text_x = x1
            text_y = y1 - 10 # Default above the box
            
            # If text goes above the frame, place it inside the box near the top
            if text_y < 10: 
                text_y = y1 + text_size[1] + 5 # Place inside, slightly below top edge
            
            cv2.putText(frame, label, (text_x, text_y), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Draw center point
            center = ((x1 + x2) // 2, (y1 + y2) // 2)
            cv2.circle(frame, center, 4, (255, 0, 0), -1) # Red center dot
            
    # Display counts on image
    display_image_counts(frame, count_by_type)
    
    # Calculate total count
    total_count = sum(count_by_type.values())
    
    return frame, total_count, count_by_type

def is_crossing_line(prev_center, curr_center, line_y):
    """Check if object crossed the counting line (for video processing)"""
    return (prev_center[1] < line_y and curr_center[1] >= line_y)

def process_video_frame_with_tracking(frame):
    """
    Process video frame with tracking and line crossing detection
    """
    global counted_ids, previous_centers, count_by_type_global

    results = model(frame, verbose=False)[0]
    detections = []

    # Extract detections for only Car, Truck, Motorcycle
    for box in results.boxes:
        cls = int(box.cls[0])
        if cls in class_names:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            if conf > 0.4:  # Apply confidence threshold
                detections.append(([x1, y1, x2 - x1, y2 - y1], conf, class_names[cls]))

    # Track using DeepSORT
    tracks = tracker.update_tracks(detections, frame=frame)

    frame_counts = {"Car": 0, "Truck": 0, "Motorcycle": 0}

    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id
        ltrb = track.to_ltrb()
        x1, y1, x2, y2 = map(int, ltrb)
        center = ((x1 + x2) // 2, (y1 + y2) // 2)

        cls_name = track.get_det_class() or "Vehicle"
        cls_name = cls_name if cls_name in ["Car", "Truck", "Motorcycle"] else "Vehicle"

        # Get previous center for this ID
        prev_center = previous_centers.get(track_id, center)

        # Count only once per ID when crossing the line (optional for video)
        # For now, we'll count all detected objects in each frame
        if track_id not in counted_ids:
            counted_ids.add(track_id)
            count_by_type_global[cls_name] += 1
            frame_counts[cls_name] += 1

        # Draw bounding box and ID
        color = get_class_color(cls_name)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f'{cls_name} ID:{track_id}', (x1, y1 - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.circle(frame, center, 4, (255, 0, 0), -1)

        # Save center for next frame
        previous_centers[track_id] = center

    return frame, frame_counts

def reset_video_counters():
    """Reset all video tracking variables"""
    global count_by_type_global, counted_ids, previous_centers
    count_by_type_global = defaultdict(int)
    counted_ids = set()
    previous_centers = {}

def detect_vehicles_from_video(video_path):
    """
    Process entire video and return final results
    This function is called by Flask app for video processing
    """
    # Reset counters for new video
    reset_video_counters()
    
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    final_frame = None
    
    # Final counts to return
    final_counts = {"Car": 0, "Truck": 0, "Motorcycle": 0}
    
    print(f"Processing video: {video_path}")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        
        # Process every 3rd frame for performance (as in original)
        if frame_count % 3 != 0:
            continue
        
        # Process frame with tracking
        processed_frame, frame_counts = process_video_frame_with_tracking(frame)
        final_frame = processed_frame
        
        # Update final counts
        for vehicle_type in final_counts:
            final_counts[vehicle_type] += frame_counts[vehicle_type]

    cap.release()
    
    # Use global counts (accumulated throughout video)
    final_counts = {
        "Car": count_by_type_global["Car"],
        "Truck": count_by_type_global["Truck"], 
        "Motorcycle": count_by_type_global["Motorcycle"]
    }
    
    # Add count display to final frame
    if final_frame is not None:
        display_image_counts(final_frame, final_counts)
    
    total_count = sum(final_counts.values())
    
    print(f"Video processing complete. Total vehicles: {total_count}")
    print(f"Breakdown: {final_counts}")
    
    return final_frame, total_count, final_counts

# Additional utility functions for standalone testing
def run_on_image(image_path):
    """Process a single static image (for standalone testing)"""
    print(f"Processing image: {image_path}")
    
    try:
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"Error: Could not load image from {image_path}")
            return None
        
        processed_frame, total_count, counts = detect_vehicles(frame)
        
        print("\n=== DETECTION RESULTS ===")
        for vehicle_type, count in counts.items():
            print(f"{vehicle_type}: {count}")
        print(f"Total Vehicles: {total_count}")
        print("========================\n")
        
        # Display the result
        cv2.imshow("Static Image Detection", processed_frame)
        print("Press any key to close the image window...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return processed_frame, total_count, counts
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def run_on_video(video_path):
    """Process video (for standalone testing)"""
    result = detect_vehicles_from_video(video_path)
    if result:
        final_frame, total_count, counts = result
        if final_frame is not None:
            cv2.imshow("Video Processing Result", final_frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    return result

# Main function for standalone testing
if __name__ == "__main__":
    # Test with image
    # run_on_image("test_image.jpg")
    
    # Test with video
    # run_on_video("test_video.mp4")
    
    print("detection_utils.py loaded successfully!")
    print("Available functions:")
    print("- detect_vehicles(frame) - for image processing")
    print("- detect_vehicles_from_video(video_path) - for video processing")
