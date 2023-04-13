import cv2
import xml.etree.ElementTree as ET
import os
import numpy as np
from shapely import union_all
from shapely.geometry import LineString
from shapely.ops import linemerge
from shapely import buffer

from shapely.geometry import LineString

# Parse the XML file
xml_file = '/home/ohm/Documents/HTWKRobots/hackingweekend/naoTeamRepo/firmware_5.0/vision/demo/annotations.xml'
tree = ET.parse(xml_file)
root = tree.getroot()

# Function to parse points from a string
def parse_points(points_str):
    points = []
    for point in points_str.split(';'):
        x, y = point.split(',')
        points.append((float(x), float(y)))
    points = np.array(points, dtype=np.int32)
    return points



gridsize = 5

# Iterate through images and draw polygons
for image_element in root.iter('image'):
    image_name = image_element.get('name')
    image_path = f'/home/ohm/FiFi/FiFi_Dataset/Selected_Pictues_2.0/Half_1/{image_name}'
    img = cv2.imread(image_path)
    ground_truth = []
    detector_output = []
    iou_array = []
    iou = 0

    if os.path.exists(image_path):
        print("Image file exists.")
    else:
        print("Image file does not exist.")
        continue

    print("lines")
    for line_element in image_element.iter('line'):
        points_str = line_element.get('points')
        points = parse_points(points_str)
        print(points)
        detector_output.append(buffer(LineString(points), 5))
        cv2.polylines(img, [points], isClosed=False, color=(0, 0, 255), thickness=2)

    print("polygons")
    for polygon_element in image_element.iter('polygon'):
        points_str = polygon_element.get('points')
        points = parse_points(points_str)
        ground_truth.append(buffer(LineString(points), 5))
        print(points)
        cv2.polylines(img, [points], isClosed=True, color=(0, 255, 0), thickness=2)
    union_all_poly = union_all(ground_truth)
    union_all_line = union_all(detector_output)
    print("union_all_poly")
    print(union_all_poly)

    print("union all lines")
    print(union_all_line)

    intersection = union_all_poly.intersection(union_all_line)
    print("intersection")
    print(intersection)
    union = union_all_poly.union(union_all_line)
    print("union")
    print(union)
    iou = intersection.length / union.length
    print("iou")
    print(iou)
    print("union")

    print("inter")
    print(intersection)

    #test = np.array([np.array(geom) for geom in linemerge(union).coords])

    #cv2.polylines(img, [test], isClosed=True, color=(255, 0, 0), thickness=2)

    print("NEW IMG")

    iou_array.append(iou)

    # Show the image with the polygons
    cv2.imshow(image_name, img)
    cv2.waitKey(0)

cv2.destroyAllWindows()