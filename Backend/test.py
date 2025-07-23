import cv2
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from collections import defaultdict

# Load YOLOv8 model
model = YOLO('yolov8n.pt')  # Replace with 'best.pt' if using custom model

# Initialize DeepSORT tracker (only for video processing)
tracker = DeepSort(max_age=30)

# Class map for COCO
class_names = {
    2: "Car",
    3: "Motorcycle", 
    7: "Truck"
}

# Global variables for video processing
count_by_type = defaultdict(int)
counted_ids = set()
previous_centers = {}

# Red line configuration for video
LINE_Y = 300  # Adjust based on your frame
LINE_OFFSET = 10  # Tolerance to detect crossing
line_thickness = 3

# ---------- COUNTING LOGIC FOR VIDEO ----------
def is_crossing_line(prev_center, curr_center, line_y):
    """Check if object crossed the counting line"""
    return (prev_center[1] < line_y and curr_center[1] >= line_y)

def process_video_frame(frame):
    """Process frame for video with line crossing detection"""
    global counted_ids, previous_centers

    results = model(frame, verbose=False)[0]
    detections = []

    # Extract detections for only Car, Truck, Motorcycle
    for box in results.boxes:
        cls = int(box.cls[0])
        if cls in class_names:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            detections.append(([x1, y1, x2 - x1, y2 - y1], conf, class_names[cls]))

    # Track using DeepSORT
    tracks = tracker.update_tracks(detections, frame=frame)

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

        # Count only once per ID when crossing the line
        if track_id not in counted_ids and is_crossing_line(prev_center, center, LINE_Y):
            counted_ids.add(track_id)
            count_by_type[cls_name] += 1

        # Draw bounding box and ID
        color = (0, 255, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f'{cls_name} ID:{track_id}', (x1, y1 - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.circle(frame, center, 4, (255, 0, 0), -1)

        # Save center for next frame
        previous_centers[track_id] = center

    # Draw red line
    cv2.line(frame, (0, LINE_Y), (frame.shape[1], LINE_Y), (0, 0, 255), line_thickness)

    # Display live counts for video
    display_video_counts(frame)
    return frame

def display_video_counts(frame):
    """Display live counts on video frame"""
    y_offset = 40
    cv2.putText(frame, f'Car: {count_by_type["Car"]}', (10, y_offset), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(frame, f'Truck: {count_by_type["Truck"]}', (10, y_offset + 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(frame, f'Motorcycle: {count_by_type["Motorcycle"]}', (10, y_offset + 60), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

# ---------- COUNTING LOGIC FOR STATIC IMAGES ----------
def process_static_image(frame):
    """Process static image - count all detected objects"""
    results = model(frame, verbose=False)[0]
    
    # Initialize counts for this image
    image_counts = defaultdict(int)
    
    # Process each detection
    for box in results.boxes:
        cls = int(box.cls[0])
        if cls in class_names:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls_name = class_names[cls]
            
            # Count this detection
            image_counts[cls_name] += 1
            
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
    display_image_counts(frame, image_counts)
    
    # Print results to console
    print("\n=== DETECTION RESULTS ===")
    total_vehicles = 0
    for vehicle_type, count in image_counts.items():
        print(f"{vehicle_type}: {count}")
        total_vehicles += count
    print(f"Total Vehicles: {total_vehicles}")
    print("========================\n")
    
    return frame, image_counts

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

# ---------- RESET FUNCTION FOR VIDEO ----------
def reset_video_counters():
    """Reset all video tracking variables"""
    global count_by_type, counted_ids, previous_centers
    count_by_type = defaultdict(int)
    counted_ids = set()
    previous_centers = {}
    print("Video counters reset!")

# ---------- RUN ON IMAGE ----------
def run_on_image(image_path):
    """Process a single static image"""
    print(f"Processing image: {image_path}")
    
    try:
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"Error: Could not load image from {image_path}")
            return
        
        processed_frame, counts = process_static_image(frame)
        
        # Display the result
        cv2.imshow("Static Image Detection", processed_frame)
        print("Press any key to close the image window...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return counts
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

# ---------- RUN ON VIDEO ----------
def run_on_video(video_path):
    """Process video with line crossing detection"""
    print(f"Processing video: {video_path}")
    print("Press 'q' to quit, 'r' to reset counters")
    
    # Reset counters before starting video
    reset_video_counters()
    
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"Error: Could not open video from {video_path}")
            return
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("End of video or failed to read frame")
                break
                
            processed_frame = process_video_frame(frame)
            cv2.imshow("Video Traffic Counting", processed_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                reset_video_counters()
                
        cap.release()
        cv2.destroyAllWindows()
        
        # Print final counts
        print("\n=== FINAL VIDEO COUNTS ===")
        for vehicle_type, count in count_by_type.items():
            print(f"{vehicle_type}: {count}")
        print("==========================\n")
        
    except Exception as e:
        print(f"Error processing video: {e}")

# ---------- BATCH IMAGE PROCESSING ----------
def run_on_multiple_images(image_paths):
    """Process multiple images and return combined results"""
    total_counts = defaultdict(int)
    
    for image_path in image_paths:
        print(f"\nProcessing: {image_path}")
        counts = run_on_image(image_path)
        if counts:
            for vehicle_type, count in counts.items():
                total_counts[vehicle_type] += count
    
    print("\n=== TOTAL COUNTS FROM ALL IMAGES ===")
    for vehicle_type, count in total_counts.items():
        print(f"{vehicle_type}: {count}")
    print("====================================\n")
    
    return total_counts

# ---------- MAIN ----------
if __name__ == "__main__":
    # === Choose your processing mode ===
    
    # For single image processing
    run_on_video("sample.mp4")
    
    # For video processing (uncomment to use)
    # run_on_video("your_video.mp4")
    
    # For multiple images (uncomment to use)
    # image_list = ["image1.jpg", "image2.jpg", "image3.jpg"]
    # run_on_multiple_images(image_list)
    
    # For testing with different image
    # run_on_image("test.jpg")