# gesture input program for first task
#pyglet application where u can draw, reset and recognize

import pyglet
from pyglet.window import mouse, key
from pyglet import shapes
from recognizer import DollarRecognizer, Point, resample_points, scale_to, translate_to, SQUARE_SIZE, ORIGIN

#pyglet 
window = pyglet.window.Window(1440, 900)
batch = pyglet.graphics.Batch()
recognized_label = pyglet.text.Label('', x=10, y=10, anchor_x='left', anchor_y='bottom')

# lists
points = []
lines = []

#recognizer
dollarRecognizer = DollarRecognizer()
recognition_in_progress = False

#drawin event in pyglet
@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global recognition_in_progress
    if buttons & mouse.LEFT and not recognition_in_progress:
        points.append(Point(float(x), float(y)))  # Convert to float as Point expects float
        if len(points) > 1:
            #draw line between points | chatgpt
            line = shapes.Line(points[-2].x, points[-2].y, points[-1].x, points[-1].y,
                               width=2, color=(255, 255, 255), batch=batch)
            lines.append(line)

@window.event
def on_draw():
    window.clear()
    batch.draw()
    recognized_label.draw()

# key press events, enter and r
@window.event
def on_key_press(symbol, modifiers):
    global points, recognition_in_progress

    if symbol == key.ENTER and not recognition_in_progress:
        start_recognition()
    
    if symbol == key.R:
        reset_everything()

def start_recognition():
    global recognition_in_progress, points

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

#run pyglet
pyglet.app.run()

