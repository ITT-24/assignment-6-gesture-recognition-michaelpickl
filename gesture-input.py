import pyglet
from pyglet.window import mouse, key
from pyglet import shapes
from recognizer import DollarRecognizer, Point, resample_points, scale_to, translate_to, SQUARE_SIZE, ORIGIN
import xml.etree.ElementTree as ET
from xml.dom import minidom
import time
import os

# Pyglet configuration
WINDOW_HEIGHT = 900
WINDOW_WIDTH = 1440
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
batch = pyglet.graphics.Batch()
recognized_label = pyglet.text.Label('', x=10, y=10, anchor_x='left', anchor_y='bottom')

# Lists
points = []
lines = []
name = 'pigtail10'

# Recognizer
dollarRecognizer = DollarRecognizer()
recognition_in_progress = False

# Drawing event in Pyglet
@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global recognition_in_progress
    if buttons & mouse.LEFT and not recognition_in_progress:
        points.append(Point(float(x), float(y)))
        if len(points) > 1:
            line = shapes.Line(points[-2].x, points[-2].y, points[-1].x, points[-1].y, width=2, color=(255, 255, 255), batch=batch)
            lines.append(line)

@window.event
def on_draw():
    window.clear()
    batch.draw()
    recognized_label.draw()

# Key press events
@window.event
def on_key_press(symbol, modifiers):
    global points, recognition_in_progress

    if symbol == key.ENTER and not recognition_in_progress:
        start_recognition()
    
    if symbol == key.R:
        reset_everything()
    
    if symbol == key.S:
        save_points_to_xml('dataset/new_dataset')

def start_recognition():
    global recognition_in_progress, points
    print(points)

    for point in points:
        y = point.y
        point.y = WINDOW_HEIGHT - y

    recognition_in_progress = True
    candidate_points = resample_points(points)
    candidate_points = scale_to(candidate_points, SQUARE_SIZE)
    candidate_points = translate_to(candidate_points, ORIGIN)
    recognized_result = dollarRecognizer.recognize(candidate_points)
    recognized_label.text = f'Recognized Gesture: {recognized_result.name}'
    recognition_in_progress = False
    points.clear()

def reset_everything():
    global points, lines, recognition_in_progress

    points.clear()
    lines.clear()

    recognition_in_progress = False
    recognized_label.text = ''

#function to save drawn shape as xml with help from chatgpt

def save_points_to_xml(filename):
    global name
    root = ET.Element("Gesture", Name=name, Subject="1", Speed="fast", Number="1", NumPts=str(len(points)), Millseconds="547", AppName="Gestures", AppVer="3.5.0.0", Date="Monday, March 05, 2007", TimeOfDay="5:05:00 PM")

    for i, point in enumerate(points):
        ET.SubElement(root, "Point", X=str(int(point.x)), Y=str(int(point.y)), T=str(i))
    
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml_as_string = reparsed.toprettyxml(indent="  ")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_as_string)
        
# Run Pyglet
pyglet.app.run()
