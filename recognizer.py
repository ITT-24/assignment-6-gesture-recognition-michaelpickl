# $1 gesture recognizer

#https://depts.washington.edu/acelab/proj/dollar/index.html
#used example codes from this website
# chat gpt helped at some math issues i got

#imports
import numpy as np
import math
import xml.etree.ElementTree as ET
from scipy.signal import resample
import os
import time

# classes infront of constants, Point need to be defined
class Point:
    def __init__(self, x, y, t = 0):
        self.x = x
        self.y = y
        self.t = t

class Rectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class Result:
    def __init__(self, name, score, time_ms):
        self.name = name
        self.Score = score
        self.Time = time_ms

#Constants
NUM_UNISTROKES = 16
NUM_POINTS = 64
SQUARE_SIZE = 250.0
DIAGONAL = math.sqrt(SQUARE_SIZE ** 2 + SQUARE_SIZE ** 2)
HALF_DIAGONAL = 0.5 * DIAGONAL
ANGLE_RANGE = math.radians(45.0)
ANGLE_PRECISION = math.radians(2.0)
PHI = 0.5 * (-1.0 + math.sqrt(5.0))  # Golden Ratio
ORIGIN = Point(0, 0)

def bounding_box(points):
    min_x = float('inf')
    max_x = float('-inf')
    min_y = float('inf')
    max_y = float('-inf')
    for point in points:
        min_x = min(min_x, point.x)
        min_y = min(min_y, point.y)
        max_x = max(max_x, point.x)
        max_y = max(max_y, point.y)
    return Rectangle(min_x, min_y, max_x - min_x, max_y - min_y)

def resample_points(points):
    points = [(point.x, point.y) for point in points]
    points = np.array(points, dtype=float)
    # resample function from scipy.signal
    points = resample(points, NUM_POINTS)
    resampled_points = []
    for (x,y) in points:
        resampled_points.append(Point(x, y))
    return resampled_points

def centroid(points):
    x = 0.0
    y = 0.0
    for i in range(0, len(points)):
        x = x + points[i].x
        y = y + points[i].y
    x = x / len(points)
    y = y / len(points)
    return Point(x, y)

def indicative_angle(points):
    c = centroid(points)
    return math.atan2(c.y - points[0].y, c.x - points[0].x)

def rotate_by(points, radians):
    c = centroid(points)
    cos = math.cos(radians)
    sin = math.sin(radians)
    new_points = []
    for i in range(0, len(points)):
        qx = (points[i].x - c.x) * cos - (points[i].y - c.y) * sin + c.x
        qy = (points[i].x - c.x) * sin + (points[i].y - c.y) * cos + c.y
        new_points.append(Point(qx, qy))
    return new_points

def scale_to(points, square_size): 
    bbox = bounding_box(points)
    new_points = []
    for point in points:
        qx = point.x * (square_size / bbox.width)
        qy = point.y * (square_size / bbox.height)
        new_points.append(Point(qx, qy))
    return new_points

def translate_to(points, origin):
    c = centroid(points)
    new_points = []
    for point in points:
        qx = point.x + origin.x - c.x
        qy = point.y + origin.y - c.y
        new_points.append(Point(qx, qy))
    return new_points

def distance(p1, p2):
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    return (dx ** 2 + dy ** 2) ** 0.5

def path_distance(pts1, pts2):
    if len(pts1) != len(pts2):
        raise ValueError("List arent the same length")
    total_distance = 0.0
    for i in range(len(pts1)):
        total_distance += distance(pts1[i], pts2[i])
    return total_distance / len(pts1)

def distance_at_angle(points, T, radians):
    rotated_points = rotate_by(points, radians)
    return path_distance(rotated_points, T.points)

def distance_at_best_angle(points, T, a, b, threshold):
    x1 = PHI * a + (1.0 - PHI) * b
    f1 = distance_at_angle(points, T, x1)
    x2 = (1.0 - PHI) * a + PHI * b
    f2 = distance_at_angle(points, T, x2)
    while abs(b - a) > threshold:
        if f1 < f2:
            b = x2
            x2 = x1
            f2 = f1
            x1 = PHI * a + (1.0 - PHI) * b
            f1 = distance_at_angle(points, T, x1)
        else:
            a = x1
            x1 = x2
            f1 = f2
            x2 = (1.0 - PHI) * a + PHI * b
            f2 = distance_at_angle(points, T, x2)
    return min(f1, f2)

class Unistroke:
    def __init__(self, name, points):
        self.name = name
        self.points = resample_points(points)
        self.radians = indicative_angle(self.points)
        self.points = rotate_by(self.points, -self.radians)
        self.points = scale_to(self.points, SQUARE_SIZE)
        self.points = translate_to(self.points, ORIGIN)

# code from given notebook
def load_templates_from_XML(path):
    unistrokes = []
    for root, subdirs, files in os.walk(path):
        if len(files) > 0:
            for f in files:
                if '.xml' in f:
                    fname = f.split('.')[0]
                    label = fname[:-2]
                    
                    xml_root = ET.parse(f'{root}/{f}').getroot()

                    points = []
                    for element in xml_root.findall('Point'):
                        x = element.get('X')
                        y = element.get('Y')
                        points.append(Point(x, y))
                    unistrokes.append(Unistroke(label, points))
    return unistrokes

class DollarRecognizer:
    def __init__(self):
        self.unistrokes = load_templates_from_XML("dataset/taskOne") #path where templates are stored

    
    def recognize(self, points):
        t0 = time.time()
        candidate = Unistroke("", points)
        u = -1
        b = float('inf')
        for i in range(len(self.unistrokes)):
            d = distance_at_best_angle(candidate.points, self.unistrokes[i], -ANGLE_RANGE, +ANGLE_RANGE, ANGLE_PRECISION)  # Golden Section Search (original $1)
            if d < b:
                b = d 
                u = i 
        t1 = time.time()
        if u == -1:
            return Result("No match.", 0.0, t1 - t0)
        else:
            score = 1.0 - b / HALF_DIAGONAL
            return Result(self.unistrokes[u].name, score, t1 - t0)
