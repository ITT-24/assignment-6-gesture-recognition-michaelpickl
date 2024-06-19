from recognizer import DollarRecognizer, resample_points, scale_to, translate_to, SQUARE_SIZE, ORIGIN, Point
import os
import xml.etree.ElementTree as ET
import time
import numpy as np

#list
points = []
times = []
correct_predictions = 0
total_attempts = 0
accuracy = 0
mean_time = 0

dollarRecognizer = DollarRecognizer()

folder_path = 'dataset/test_set' 

def extract_gesture_data(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    gesture_name = root.get('Name')
    points = []
    
    for point in root.findall('.//Point'):
        x = int(point.get('X'))
        y = int(point.get('Y'))
        points.append(Point(x, y))
    
    return gesture_name, points

def read_gestures_from_folder(folder_path):
    gesture_data = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.xml'):
            file_path = os.path.join(folder_path, filename)
            gesture_name, points = extract_gesture_data(file_path)
            gesture_data.append((gesture_name, points))
    
    return gesture_data

points = read_gestures_from_folder(folder_path)

start_time = time.time()
for name, point in points:
    resampled_points = resample_points(point)
    resampled_points = scale_to(resampled_points, SQUARE_SIZE)
    resampled_points = translate_to(resampled_points, ORIGIN)
    recognized_result = dollarRecognizer.recognize(resampled_points)

    expected_result = name[:-2]
    if recognized_result.name == expected_result:
        correct_predictions += 1
    total_attempts += 1

end_time = time.time()
recognize_time = end_time - start_time
times.append(recognize_time)

accuracy = correct_predictions / total_attempts

mean_time = np.mean(times)

def return_time():
    global mean_time
    return mean_time

def return_accuracy():
    global accuracy
    return accuracy

print(accuracy)
print(mean_time)

