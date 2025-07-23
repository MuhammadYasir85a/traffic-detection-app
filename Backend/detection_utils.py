# detection_utils.py
import cv2
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from collections import defaultdict

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
    # Create a semi-transparent overlay for better text visibility
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (300, 120), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Display counts
    y_offset = 40
    cv2.putText(frame, "VEHICLE COUNT:", (15, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cv2.putText(frame, f'Cars: {counts["Car"]}', (15, y_offset + 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, f'Trucks: {counts["Truck"]}', (15, y_offset + 45), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    cv2.putText(frame, f'Motorcycles: {counts["Motorcycle"]}', (15, y_offset + 70), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    total = sum(counts.values())
    cv2.putText(frame, f'Total: {total}', (15, y_offset + 95), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

def detect_vehicles(frame):
    """
    Process static image - count all detected objects
    This function is called by Flask app for single image processing
    """
    results = model(frame, verbose=False)[0]
    
    # Initialize counts for this image
    count_by_type = {"Car": 0, "Truck": 0, "Motorcycle": 0}
    
    # Process each detection
    for box in results.boxes:
        cls = int(box.cls[0])
        if cls in class_names:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls_name = class_names[cls]
            
            # Only count if confidence is above threshold
            if conf > 0.4:
                # Count this detection
                count_by_type[cls_name] += 1
                
                # Draw bounding box
                color = get_class_color(cls_name)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw class name and confidence
                label = f'{cls_name}: {conf:.2f}'
                cv2.putText(frame, label, (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # Draw center point
                center = ((x1 + x2) // 2, (y1 + y2) // 2)
                cv2.circle(frame, center, 4, (255, 0, 0), -1)
    
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