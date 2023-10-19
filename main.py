import cv2
import numpy as np
from ultralytics import YOLO
from utills import get_limits
from PIL import Image
import os
import time
from util import read_license_plate
import pyrebase
from firebase_admin import storage
from firebase_admin import db
import datetime
import requests

light_violation1 = 'images/traffic_light/number_plate'
if not os.path.exists(light_violation1):
    os.makedirs(light_violation1)
light_violation2 = 'images/traffic_light/frame'
if not os.path.exists(light_violation2):
    os.makedirs(light_violation2)
light_violation3 = 'images/traffic_light/vehicle'
if not os.path.exists(light_violation3):
    os.makedirs(light_violation3)

direct_violate1 = 'images/direction_violation/number_plate'
if not os.path.exists(direct_violate1):
    os.makedirs(direct_violate1)
direct_violate2 = 'images/direction_violation/frame'
if not os.path.exists(direct_violate2):
    os.makedirs(direct_violate2)

direct_violate3 = 'images/direction_violation/vehicle'
if not os.path.exists(direct_violate3):
    os.makedirs(direct_violate3)

def create_mj(id_mapping, plate_mapping, vehicle_class):
    mj = {}  # Create the 'mj' dictionary
    vls = vehicle_class
    for i, (vid, box) in enumerate(id_mapping.items()):  # Use 'enumerate' to get both index 'i' and value 'vid'
        x1, y1, x2, y2, conf1 = box
        vehicle = vid

        if not plate_mapping:
            mj[vehicle] = (x1, y1, x2, y2, conf1, vls[i])  # Use index 'i' to access 'vehicle_class'

        else:
            for pid, pbox in plate_mapping.items():
                x3, y3, x4, y4, conf2 = pbox
                if x1 < x3 and x4 < x2 and y1 < y3 and y4 < y2:
                    mj[vehicle] = (
                    x1, y1, x2, y2, conf1, x3, y3, x4, y4, conf2, vls[i])  # Use index 'i' to access 'vehicle_class'
                else:
                    mj[vehicle] = (x1, y1, x2, y2, conf1, vls[i])  # Use index 'i' to access 'vehicle_class'
    return mj

def track_plate_id(plate):
    input = plate
    for res in input:
        if res.id != None:
            track_id = res.id.int().cpu().tolist()
            return track_id

def newassign_ids_and_coordinates_to_tracked_objects(boxes, v_track_id, v_det_conf):
    if v_track_id is None:
        return {}

    if len(boxes) != len(v_track_id) or len(boxes) != len(v_det_conf):
        raise ValueError("Number of boxes, IDs, and detection confidences must be the same.")

    id_coord_mapping = {}

    for i in range(len(boxes)):
        box = boxes[i]
        x1, y1, x2, y2 = box
        id_mapping = v_track_id[i]
        det_conf = v_det_conf[i]  # Get the detection confidence value
        # Include the detection confidence value in the tuple
        id_coord_mapping[id_mapping] = (x1, y1, x2, y2, det_conf)
    return id_coord_mapping
def detect_green_color(frame):
    traffic_signal = [(849, 27), (846, 90), (871, 91), (873, 26)]
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

    cv2.polylines(frame, [np.array(traffic_signal, np.int32)], True, (0, 0, 255), 2)

    return bbox is not None
#firebase
config = {
  'apiKey': "AIzaSyD_NFy6pD8-gnQJUMqKbPF8qux7IYz8H_g",
  'authDomain': "research-project-811a8.firebaseapp.com",
  'databaseURL': "https://research-project-811a8-default-rtdb.asia-southeast1.firebasedatabase.app",
  'projectId': "research-project-811a8",
  'storageBucket': "research-project-811a8.appspot.com",
  'messagingSenderId': "792324726693",
  'appId': "1:792324726693:web:94ef9d2bc5d1558724924c",
  'measurementId': "G-77N9TYF9N3",
  'serviceAccount': "credentials.json",
}

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
db = firebase.database()

#get time
# now = datetime.now()
# current_time = now.strftime("%H:%M:%S")

#set location
location = "https://www.google.com/maps/place/Welipenna+Interchange/@6.452543,80.0863553,17z/data=!3m1!4b1!4m6!3m5!1s0x3ae22d305126dacb:0xb503df7f647ef4cd!8m2!3d6.4525377!4d80.0889302!16s%2Fg%2F11hbv9y3dn?entry=ttu"

# variables
offset = 6
go_up = {}
red_light = {}
red_light_counter = []
up_counter = []
red_light_violation_area = [(640,341), (847,426), (971, 392), (765, 331)]
vehicle_types = [2]
down = {}
down_counter_direction = []
model = YOLO('yolov8l.pt')
p_model = YOLO('last.pt')
video_path = "Red_light_3.mp4"
cap = cv2.VideoCapture(video_path)
light_violated_count = []

api_url = 'http://localhost:8060/violation/new'
cam_id = 'CAM_001'

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
        v_con_level = results[0].boxes.conf.cpu().tolist()
        vehicle_det_conf = [int(value * 100) for value in v_con_level]

        # Run YOLOv8 tracking on the frame to detect number plates
        plate_result = p_model.track(frame, persist=True)
        # Get the boxes, class, and ID of number plates
        p_boxes = plate_result[0].boxes.xyxy.int().cpu().tolist()
        p_track_id = track_plate_id(plate_result[0].boxes)
        p_con_level = plate_result[0].boxes.conf.cpu().tolist()
        plate_det_conf = [int(value * 100) for value in p_con_level]

        # Call assign_ids_and_coordinates_to_tracked_objects function to assign IDs and coordinates to tracked number plates
        id_mapping = newassign_ids_and_coordinates_to_tracked_objects(boxes, v_track_id, vehicle_det_conf)

        # Call assign_ids_and_coordinates_to_tracked_objects function to assign IDs and coordinates to tracked number plates
        plate_mapping = newassign_ids_and_coordinates_to_tracked_objects(p_boxes, p_track_id, plate_det_conf)

        # tracked vehicle with number plate coordinates
        mj = create_mj(id_mapping, plate_mapping, vehicle_class)
        detected_green = detect_green_color(frame)
        image_counter = 0

        for id_, value, in mj.items():
            x1, y1, x2, y2, conf1, x3, y3, x4, y4, conf2, clsid = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            v_id = 0
            c_x, c_y, pc_x, pc_y = 0, 0, 0, 0
            if len(value) == 6:
                x1, y1, x2, y2, conf1, clsid = value
                v_id = id_
                c_x = x1 + (x2 - x1) // 2
                c_y = y1 + (y2 - y1) // 2
            elif len(value) == 11:
                x1, y1, x2, y2, conf1, x3, y3, x4, y4, conf2, clsid = value
                v_id = id_
                c_x = x1 + (x2 - x1) // 2
                c_y = y1 + (y2 - y1) // 2
                pc_x = x3 + (x3 - x4) // 2
                pc_y = y3 + (y3 - y4) // 2

        #traffic light violation detection
            red_light_violation_detection = cv2.pointPolygonTest(np.array(red_light_violation_area, np.int32), ((c_x, c_y)), False)
            if detected_green == True:
                cv2.polylines(frame, [np.array(red_light_violation_area, np.int32)], True, (0, 0, 255), 1)
                if red_light_violation_detection >= 0 and conf1>60:

                    current_time = time.ctime()

                    cv2.circle(frame, (c_x, c_y), 2, (0, 0, 255), -1)
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
                    cv2.rectangle(frame, (int(x3), int(y3)), (int(x4), int(y4)), (255, 0, 0), 2)
                    #cv2.putText(frame, str(v_id), (x1, y1 - 2), 0, 1, (255, 255, 255), thickness=1, lineType=cv2.LINE_AA)
                    frame_image_filename = os.path.join(light_violation2, f'traffic_light_{v_id}.jpg')
                    image_trafficlight_frame = os.path.join(light_violation2, f'traffic_light_{v_id}.jpg')
                    data_redlight={"violation":"redlight_violation","ID":v_id,"Time":current_time,"Location":location}
                    cv2.imwrite(frame_image_filename, frame)
                    storage.child(image_trafficlight_frame).put(image_trafficlight_frame)
                    db.child("Violation_Details").child(v_id).set(data_redlight)
                    red_light[v_id] = c_y
                    noi_redlight={"NOI":len(red_light)}
                    db.child("NumberOf_redlight_violation").set(noi_redlight)
                    #vehicle
                    RLV_vehicle_crop = frame[int(y1):int(y2), int(x1):int(x2), :]
                    RLV_vehicle_image_filename = os.path.join(light_violation3, f'traffic_light_{v_id}.jpg')
                    image_trafficlight_vehicle = os.path.join(light_violation1, f'traffic_light_{v_id}.jpg')
                    cv2.imwrite(RLV_vehicle_image_filename, RLV_vehicle_crop)
                    #storage.child(image_trafficlight_vehicle).put(image_trafficlight_vehicle)

                    #plate
                    RLV_plate_crop = frame[int(y3):int(y4), int(x3):int(x4), :]
                    RLV_plate_image_filename = os.path.join(light_violation1, f'traffic_light_{v_id}.jpg')
                    #image_trafficlight_plate = os.path.join(light_violation1, f'traffic_light_{v_id}.jpg')

                    # Send the image to the Node.js server via API
                    date = datetime.date.today()
                    # current_time = time.ctime()
                    files = {'file': open(RLV_vehicle_image_filename, 'rb')}
                    data = {
                        'type': 'red light violation',
                        'year': str(date.year),
                        'month': str(date.month),
                        'day': str(date.day),
                        'time': str(current_time),
                        'location': location,
                        'camId': cam_id
                    }
                    response = requests.post(api_url, data=data, files=files)
                    print(response.text)

                    if RLV_plate_crop is not None and not RLV_plate_crop.size == 0:
                        cv2.imwrite(RLV_plate_image_filename, RLV_plate_crop)
                        #storage.child(image_trafficlight_plate).put(image_trafficlight_plate)
                        cv2.imshow('red light violated vehicle plates', RLV_plate_crop)
                        RLV_plate_crop_gray = cv2.cvtColor(RLV_plate_crop, cv2.COLOR_BGR2GRAY)
                        _, plate_crop_thresh = cv2.threshold(RLV_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)
                        plate_text, plate_confident_val = read_license_plate(plate_crop_thresh)
                        print(plate_text)

        # direction violation
            if 150 < (c_x + offset) and 150 > (c_x - offset) and c_y > 415 and c_y < 584 and (clsid in vehicle_types) and conf1 > 60:
                down[v_id] = time.time()
            if v_id in down:
                if 378 < (c_x + offset) and 378 > (c_x - offset):
                    get_down = time.time() - down[v_id]
                    distance = 10
                    down_speed = (distance / get_down) * 3.6
                    if (down_speed > 0) and down_counter_direction.count(v_id) == 0:
                        down_counter_direction.append(v_id)
                        noi_direction={"NOI":len(down_counter_direction)}
                        db.child("NumberOf_direction_violation").set(noi_direction)
                for val in down_counter_direction:
                    for key, value in mj.items():
                        if val == key:
                            sx1, sy1, sx2, sy2, sconf1, sx3, sy3, sx4, sy4, sconf2, sclsid = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                            sv_id = 0
                            sc_x, sc_y, spc_x, spc_y = 0, 0, 0, 0
                            if len(value) == 6:
                                current_time = time.ctime()
                                sx1, sy1, sx2, sy2, sconf1, sclsid = value
                                sv_id = val
                                sc_x = sx1 + (sx2 - sx1) // 2
                                sc_y = sy1 + (sy2 - sy1) // 2
                                frame_image_filename = os.path.join(direct_violate2, f'direction_{v_id}.jpg')
                                image_direction_frame = os.path.join(direct_violate2, f'direction_{v_id}.jpg')
                                data_direction={"violation":"direction_violation","ID":v_id,"Time":current_time,"Location":location}
                                cv2.imwrite(frame_image_filename, frame)
                                storage.child(image_direction_frame).put(image_direction_frame)
                                db.child("Violation_Details").child(v_id).set(data_direction)
                                # vehicle
                                DVP_vehicle_crop = frame[int(y1):int(y2), int(x1):int(x2), :]
                                DVP_vehicle_image_filename = os.path.join(direct_violate3, f'direction_{v_id}.jpg')
                                image_direction_violation_vehicle = os.path.join(light_violation1, f'direction_{v_id}.jpg')
                                cv2.imwrite(DVP_vehicle_image_filename, DVP_vehicle_crop)
                                storage.child(image_direction_violation_vehicle).put(image_direction_violation_vehicle)
                            elif len(value) == 11:
                                sx1, sy1, sx2, sy2, sconf1, sx3, sy3, sx4, sy4, sconf2, sclsid = value
                                sv_id = val
                                sc_x = sx1 + (sx2 - sx1) // 2
                                sc_y = sy1 + (sy2 - sy1) // 2
                                spc_x = sx3 + (sx3 - sx4) // 2
                                spc_y = sy3 + (sy3 - sy4) // 2
                                # crop license plate
                                DVP_plate_crop = frame[int(sy3):int(sy4), int(sx3):int(sx4), :]
                                plate_image_filename = os.path.join(direct_violate1, f'direction_{v_id}.jpg')
                                image_direction_plate = os.path.join(direct_violate1, f'direction_{v_id}.jpg')
                                frame_image_filename = os.path.join(direct_violate2, f'direction_{v_id}.jpg')
                                image_direction_frame = os.path.join(direct_violate2, f'direction_{v_id}.jpg')
                                # vehicle
                                DVP_vehicle_crop = frame[int(y1):int(y2), int(x1):int(x2), :]
                                DVP_vehicle_image_filename = os.path.join(direct_violate3, f'direction_{v_id}.jpg')
                                image_direction_violation_vehicle = os.path.join(light_violation1, f'direction_{v_id}.jpg')
                                cv2.imwrite(DVP_vehicle_image_filename, DVP_vehicle_crop)
                                storage.child(image_direction_violation_vehicle).put(image_direction_violation_vehicle)
                                if DVP_plate_crop is not None and not DVP_plate_crop.size == 0:
                                    cv2.imshow("frame", DVP_plate_crop)
                                    cv2.imwrite(plate_image_filename, DVP_plate_crop)
                                    storage.child(image_direction_plate).put(image_direction_plate)
                                    cv2.imwrite(frame_image_filename, frame)
                                    storage.child(image_direction_frame).put(image_direction_frame)
                                    DVP_plate_crop_gray = cv2.cvtColor(DVP_plate_crop, cv2.COLOR_BGR2GRAY)
                                    _, plate_crop_thresh = cv2.threshold(DVP_plate_crop_gray, 64, 255,cv2.THRESH_BINARY_INV)
                                    plate_text, plate_confident_val = read_license_plate(plate_crop_thresh)
                                    print(plate_text)
                            cv2.circle(frame, (sc_x, sc_y), 2, (0, 0, 255), -1)
                            cv2.rectangle(frame, (int(sx1), int(sy1)), (int(sx2), int(sy2)), (255, 0, 0), 2)
                            cv2.rectangle(frame, (int(sx3), int(sy3)), (int(sx4), int(sy4)), (255, 0, 0), 2)

        cv2.line(frame, (152, 504), (336, 598), (255, 255, 0), 1)
        cv2.line(frame, (575, 448), (761, 554), (255, 255, 0), 1)
        cv2.imshow("YOLOv8 Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break
# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()
9