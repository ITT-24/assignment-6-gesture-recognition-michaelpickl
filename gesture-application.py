import pyglet
from pyglet.window import mouse, key
from pyglet import shapes
from recognizer import Point
import xml.etree.ElementTree as ET
import keras
import numpy as np
import os
import joblib

# Pyglet configuration
WINDOW_HEIGHT = 900
WINDOW_WIDTH = 1440
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
batch = pyglet.graphics.Batch()
recognized_label = pyglet.text.Label('', x=10, y=10, anchor_x='left', anchor_y='bottom')

# Lists
points = []
dots = []
gestures = ['dataset/taskOne/arrow01.xml', 'dataset/taskOne/check01.xml', 'dataset/taskOne/delete_mark01.xml', 'dataset/taskOne/star01.xml']
current_gesture = 0
current_label = ''

# Recognizer
recognition_in_progress = False
model = keras.models.load_model('model_one.h5')

# Colors
colors = {'1': (255, 0, 0), '2': (0, 255, 0), '3': (0, 0, 255)}
selected_color = None

# Labels
initial_label = pyglet.text.Label(
    'Choose a House',
    x=WINDOW_WIDTH // 4, y=WINDOW_HEIGHT // 2 + 50,  # Adjusted for left side
    anchor_x='center', anchor_y='center',
    font_size=30,
    color=(255, 255, 255, 255)
)
color_prompt_label = pyglet.text.Label(
    '',
    x=WINDOW_WIDTH // 4, y=WINDOW_HEIGHT // 2,  # Adjusted for left side
    anchor_x='center', anchor_y='center',
    font_size=24,
    color=(255, 255, 255, 255)
)

# Drawing event in Pyglet
@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global recognition_in_progress
    if buttons & mouse.LEFT and not recognition_in_progress and selected_color:
        points.append([float(x), float(y)])
        if len(points) > 1:
            dots.append(shapes.Circle(x, y, 3, color=selected_color, batch=batch))

@window.event
def on_draw():
    window.clear()
    batch.draw()
    if not selected_color:
        initial_label.draw()
        color_prompt_label.draw()
    else:
        for dot in dots:
            dot.draw()
    recognized_label.draw()

# Key press events
@window.event
def on_key_press(symbol, modifiers):
    global points, recognition_in_progress, selected_color, load_gesture

    if symbol in (key._1, key._2, key._3) and not selected_color:
        selected_color = colors.get(str(symbol - key._0), None)
        if selected_color:
            initial_label.text = ''
            color_prompt_label.text = ''
            load_gesture = get_gesture()
    
            load_points_from_xml(load_gesture)
    
    if selected_color:
        if symbol == key.ENTER and not recognition_in_progress:
            start_recognition()
        
        if symbol == key.R:
            reset_everything()

def start_recognition():
    global recognition_in_progress, points, current_label
    prediction = model.predict(np.array([points])) # hier model ändern
    prediction = np.argmax(prediction)

    encoder = joblib.load('label_encoder.pkl')
    prediction_label = encoder.inverse_transform(np.array([prediction]))[0]
    print(current_label[:-2])
    print(prediction_label)
    
def reset_everything():
    global points, dots, recognition_in_progress

    points.clear()
    dots.clear()

    recognition_in_progress = False
    recognized_label.text = ''

def load_points_from_xml(file_path):
    global points, dots, selected_color, current_label
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    points.clear()
    dots.clear()

    current_label = root.attrib['Name']
    
    for point in root.findall('Point'):
        x = float(point.get('X'))
        y = float(point.get('Y'))
        points.append([x, y])
        dots.append(shapes.Circle(x, y, 3, color=selected_color, batch=batch))

# Update the label after 5 seconds
def update_label(dt):
    initial_label.text = ''
    color_prompt_label.text = 'Press 1 for Red, 2 for Green, 3 for Blue'

def get_gesture():
    global current_gesture
    current_gesture_load = gestures[current_gesture]
    current_gesture += 1
    return current_gesture_load

# Schedule the label update
pyglet.clock.schedule_once(update_label, 5)

# Example usage
# Call load_points_from_xml with the path to your XML file
# load_points_from_xml('path_to_your_file.xml')

# Run Pyglet
pyglet.app.run()
