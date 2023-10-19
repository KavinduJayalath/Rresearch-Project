import numpy as np
from ultralytics import YOLO
import cv2
import util
from sort.sort import *
from util import  get_car, read_license_plate , write_csv
import torch
from utills import get_limits
from PIL import Image

def detect_green_color(frame):
    anpr_area1 = [(345, 116), (344, 183), (372, 184), (372, 113)]
    green = [0, 0, 255]

    plate_crop = frame[116:183, 345:372, :]
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

#variables
frame_results = {}
output_result = {}
vehicles = [1,2,3]
v_tracker = Sort()
anpr_area1 = [(380,481),(129,594),(912,593),(754,481)]
area1 = [(504,192),(513,299),(593,297),(578,192)]

#load model
v_model = YOLO('yolov8l.pt')
p_model = YOLO('last.pt')

#load video
cap = cv2.VideoCapture('Front.mp4')

#read frames
frame_nmr = -1
ret = True
while ret:
    frame_nmr += 1
    ret, frame = cap.read()
    frame = cv2.resize(frame, (1020, 600))
    if ret:
        frame_results[frame_nmr] = {}
        v_results = v_model(frame)[0]
        v_detections = []
        detected_green = detect_green_color(frame)
        for detection in v_results.boxes.data.tolist():
            x1,y1,x2,y2,score,class_id = detection
            c_x = x1+ (x2 - x1)/2
            c_y = y1+(y2 - y1)/2
            anp_track_results = cv2.pointPolygonTest(np.array(anpr_area1, np.int32), ((c_x, c_y)), False)
            if detected_green == True:
                cv2.polylines(frame, [np.array(anpr_area1, np.int32)], True, (255, 255, 0), 1)
            if (class_id in vehicles) and anp_track_results >= 0 and detected_green == True:
                v_detections.append([x1, y1, x2, y2, score])
                cv2.circle(frame, (int(c_x), int(c_y)), 2, (0, 0, 255), -1)
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
                #track vehicle
                v_track_id = v_tracker.update(np.asarray(v_detections))

                #detect license plate
                p_results = p_model(frame)[0]

                for p_result in p_results.boxes.data.tolist():
                    x1,y1,x2,y2,score,class_id = p_result
                    #assign license plate for car
                    px1,py1,px2,py2,car_id = get_car(p_result,v_track_id)
                    pc_x = x1 + (x2 - x1) / 2
                    pc_y = y1 + (y2 - y1) / 2
                    #crop license plae
                    plate_crop=None
                    if (pc_x > 124 and pc_x < 912 and pc_y < 593 and pc_y > 415):
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
                        plate_crop = frame[int(y1):int(y2),int(x1):int(x2),:]

                    #process license pale
                        plate_crop_gray = cv2.cvtColor(plate_crop,cv2.COLOR_BGR2GRAY)
                        _,plate_crop_thresh = cv2.threshold(plate_crop_gray,64,255,cv2.THRESH_BINARY_INV)

                        cv2.imshow('original',plate_crop)
                        #read licence plate numbers
                        plate_text,plate_confident_val = read_license_plate(plate_crop_thresh)
                        print(plate_text)

    #cv2.polylines(frame, [np.array(anpr_area1, np.int32)], True, (255, 255, 0), 1)
    cv2.imshow("FRAME", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

write_csv(frame_results, 'D:/yolov8/new_test.csv')
cap.release()
cv2.destroyAllWindows()

