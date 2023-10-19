from collections import defaultdict
import cv2
import numpy as np
from util import get_car, read_license_plate
from functions import track_plate_id
from functions import print_ids_for_center_boxes_above_y2_threshold
from functions import assign_ids_and_coordinates_to_tracked_objects, assign_vehicle_id_to_number_plate, get_car
from ultralytics import YOLO
from utills import get_limits
from functions import assign_ids_to_boxes
from PIL import Image

offset = 6
go_up = {}
red_light = {}
red_light_counter = []
up_counter = []
# area1 = [(651,353),(816,420),(990,368),(854,307)]
# anpr_area1 = [(380,481),(129,594),(912,593),(754,481)]
are = [(535, 367), (777, 440), (971, 392), (765, 331)]

def detect_green_color(frame):
    anpr_area1 = [(849, 27), (846, 90), (871, 91), (873, 26)]
    green = [0, 0, 255]
    plate_crop = frame[27:90, 849:871, :]
    hsvImg = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2HSV)
    lower_limit, upper_limit = get_limits(color=green)
    mask = cv2.inRange(hsvImg, lower_limit, upper_limit)
    mask_ = Image.fromarray(mask)
    bbox = mask_.getbbox()

    if bbox is not None:
        x1, y1, x2, y2 = bbox
        plate_crop = cv2.rectangle(plate_crop, (x1, y1), (x2, y2), (255, 0, 0), 1)

    cv2.polylines(frame, [np.array(anpr_area1, np.int32)], True, (255, 255, 0), 1)

    return bbox is not None


# variables
vehicle_types = [2]
# Load the YOLOv8 model
model = YOLO('yolov8l.pt')
p_model = YOLO('last.pt')
# Open the video file
video_path = "Side_1.mp4"
cap = cv2.VideoCapture(video_path)
# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()
    frame = cv2.resize(frame, (1020, 600))
    if success:
        # Run YOLOv8 tracking on the frame to detect vehicles
        results = model.track(frame, persist=True)
        # Get the boxes, class and id of vehicles
        boxes = results[0].boxes.xyxy.int().cpu().tolist()
        vehicle_class = results[0].boxes.cls.int().cpu().tolist()
        v_track_id = results[0].boxes.id.int().cpu().tolist()
        # Run YOLOv8 tracking on the frame to detect number plates
        plate_result = p_model.track(frame, persist=True)
        # Get the boxes, class and id of number plate
        p_boxes = plate_result[0].boxes.xyxy.int().cpu().tolist()
        p_track_id = track_plate_id(plate_result[0].boxes)
        # Call the function to assign IDs and coordinates to tracked objects
        id_mapping = assign_ids_and_coordinates_to_tracked_objects(boxes, v_track_id)
        detected_green = detect_green_color(frame)
        print(detected_green)

        for box, (id, x1, y1, x2, y2) in id_mapping.items():
            x1, y1, x2, y2 = box
            v_id = id
            c_x = x1 + (x2 - x1) // 2
            c_y = y1 + (y2 - y1) // 2

            anp_track_results = cv2.pointPolygonTest(np.array(are, np.int32), ((c_x, c_y)), False)
            if detected_green == True:
                cv2.polylines(frame, [np.array(are, np.int32)], True, (255, 255, 0), 1)
            if anp_track_results >= 0 and detected_green == True:
                cv2.circle(frame, (c_x, c_y), 2, (0, 0, 255), -1)
                cv2.putText(frame, str(id), (x1, y1 - 2), 0, 1, (255, 255, 255), thickness=1, lineType=cv2.LINE_AA)
                red_light[id] = c_y
                if red_light_counter.count(id) == 0:
                    red_light_counter.append(id)

            if 150 < (c_x + offset) and 150 > (c_x - offset) and c_y > 415 and c_y < 584:
                go_up[id] = c_y
            if id in go_up:
                if 378 < (c_x + offset) and 378 > (c_x - offset):
                    # cv2.circle(frame, (c_x, c_y), 2, (0, 0, 255), -1)
                    # cv2.putText(frame, str(id), (218,93 - 2), 0, 1, (255, 255, 255), thickness=1, lineType=cv2.LINE_AA)
                    if up_counter.count(id) == 0:
                        up_counter.append(id)

        # cv2.line(frame, (150, 300), (150, 505), (255, 255, 0), 1)
        # cv2.line(frame, (378, 300), (378, 505), (255, 255, 0), 1)
        cv2.line(frame, (278, 476), (466, 598), (255, 255, 0), 1)
        cv2.line(frame, (575, 448), (761, 554), (255, 255, 0), 1)
        # cv2.polylines(frame, [np.array(are, np.int32)], True, (255, 255, 0), 1)
        up_vehicle_count = len(up_counter)
        red_light_count = len(red_light_counter)
        print(up_vehicle_count)
        cv2.putText(frame, ('right side wrongway = ') + str(up_vehicle_count), (218, 93), cv2.FONT_HERSHEY_PLAIN, 1,
                    (255, 255, 255), 2)
        cv2.putText(frame, ('red light counter = ') + str(red_light_count), (218, 123), cv2.FONT_HERSHEY_PLAIN, 1,
                    (255, 255, 255), 2)

        # Display the annotated frame
        cv2.imshow("YOLOv8 Tracking", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()
