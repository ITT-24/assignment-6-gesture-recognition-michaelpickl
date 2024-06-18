from recognizer import DollarRecognizer, resample_points, scale_to, translate_to, SQUARE_SIZE, ORIGIN, Point

#list
points = []
correct_predictions = 0
total_attempts = 0
accuracy = 0

dollarRecognizer = DollarRecognizer()


import os
import xml.etree.ElementTree as ET

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

# Example usage
folder_path = 'dataset/test' 
points = read_gestures_from_folder(folder_path)




for name, point in points:
    resampled_points = resample_points(point)
    resampled_points = scale_to(resampled_points, SQUARE_SIZE)
    resampled_points = translate_to(resampled_points, ORIGIN)
    recognized_result = dollarRecognizer.recognize(resampled_points)

    expected_result = name[:-2] # Replace with your expected gesture name
    if recognized_result.name == expected_result:
        correct_predictions += 1
    total_attempts += 1

accuracy = correct_predictions / total_attempts
print(accuracy)

