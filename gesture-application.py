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

# Colors
colors = {'1': (255, 0, 0), '2': (0, 255, 0), '3': (0, 0, 255)}
selected_color = None

# Labels
initial_label = pyglet.text.Label(
    'Choose a House',
    x=WINDOW_WIDTH // 2, y=WINDOW_HEIGHT // 2 + 50,
    anchor_x='center', anchor_y='center',
    font_size=30,
    color=(255, 255, 255, 255)
)
color_prompt_label = pyglet.text.Label(
    '',
    x=WINDOW_WIDTH // 2, y=WINDOW_HEIGHT // 2,
    anchor_x='center', anchor_y='center',
    font_size=24,
    color=(255, 255, 255, 255)
)

# Drawing event in Pyglet
@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global recognition_in_progress
    if buttons & mouse.LEFT and not recognition_in_progress and selected_color:
        points.append(Point(float(x), float(y)))
        if len(points) > 1:
            line = shapes.Line(
                points[-2].x, points[-2].y, 
                points[-1].x, points[-1].y, 
                width=2, color=selected_color, batch=batch
            )
            lines.append(line)

@window.event
def on_draw():
    window.clear()
    batch.draw()
    if not selected_color:
        initial_label.draw()
        color_prompt_label.draw()
    recognized_label.draw()

# Key press events
@window.event
def on_key_press(symbol, modifiers):
    global points, recognition_in_progress, selected_color

    if symbol in (key._1, key._2, key._3) and not selected_color:
        selected_color = colors[str(symbol - key._0)]
        initial_label.text = ''
        color_prompt_label.text = ''
    
    if selected_color:
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

def save_points_to_xml(directory):
    global points, name

    if not os.path.exists(directory):
        os.makedirs(directory)

    root = ET.Element("Gesture")
    root.set("Name", name)
    root.set("NumPts", str(len(points)))

    for point in points:
        pt = ET.SubElement(root, "Point")
        pt.set("X", str(point.x))
        pt.set("Y", str(point.y))

    tree = ET.ElementTree(root)
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open(f"{directory}/{name}.xml", "w") as f:
        f.write(xml_str)

# Update the label after 5 seconds
def update_label(dt):
    initial_label.text = ''
    color_prompt_label.text = 'Press 1 for Red, 2 for Green, 3 for Blue'

# Schedule the label update
pyglet.clock.schedule_once(update_label, 5)

# Run Pyglet
pyglet.app.run()
