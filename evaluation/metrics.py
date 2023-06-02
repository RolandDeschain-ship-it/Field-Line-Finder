import cv2
import os
import numpy as np
from shapely.ops import unary_union

from shapely.geometry import LineString

buffer_size = 5


# Function to parse points from a string
def parse_points(points_str):
    points = []
    for point in points_str.split(';'):
        x, y = point.split(',')
        points.append((float(x), float(y)))
    points = np.array(points, dtype=np.int32)
    return points


def calc_metrics(element):
    ground_truth = []
    detector_output = []
    iou = 0

    for line_element in element.iter('line'):
        points_str = line_element.get('points')
        points = parse_points(points_str)
        detector_output.append(LineString(points).buffer(buffer_size))

    for polygon_element in element.iter('polygon'):
        points_str = polygon_element.get('points')
        points = parse_points(points_str)
        points = np.append(points, [points[0]], axis=0)
        for point_idx, ele in np.ndenumerate(points):
            point_idx = point_idx[0]
            ground_truth.append(
                LineString([points[point_idx], points[(point_idx + 1) % len(points)]]).buffer(buffer_size))

    union_all_poly = unary_union(ground_truth)
    union_all_line = unary_union(detector_output)

    intersection = union_all_poly.intersection(union_all_line)

    union = union_all_poly.union(union_all_line)

    iou = intersection.area / union.area

    # calculate false positives area
    # get the area where the detector output is not in the ground truth
    diff = calc_false_positives(element)

    return diff, iou


def calc_false_positives(ele):
    ground_truth = []
    detector_output = []

    for line_element in ele.iter('line'):
        points_str = line_element.get('points')
        points = parse_points(points_str)
        detector_output.append(LineString(points))

    for polygon_element in ele.iter('polygon'):
        points_str = polygon_element.get('points')
        points = parse_points(points_str)
        points = np.append(points, [points[0]], axis=0)
        for point_idx, ele in np.ndenumerate(points):
            point_idx = point_idx[0]
            ground_truth.append(
                LineString([points[point_idx], points[(point_idx + 1) % len(points)]]).buffer(buffer_size + 4))

    # calculate the lenght of the detector_output lines that are not in the ground_truth polygons
    diff = unary_union(detector_output).difference(unary_union(ground_truth))

    return diff.length


# a function to calculate the false negatives
def calc_false_negatives(element):
    ground_truth = []
    detector_output = []

    for line_element in element.iter('line'):
        points_str = line_element.get('points')
        points = parse_points(points_str)
        detector_output.append(LineString(points))

    for polygon_element in element.iter('polygon'):
        points_str = polygon_element.get('points')
        points = parse_points(points_str)
        points = np.append(points, [points[0]], axis=0)
        for point_idx, ele in np.ndenumerate(points):
            point_idx = point_idx[0]
            ground_truth.append(
                LineString([points[point_idx], points[(point_idx + 1) % len(points)]]).buffer(buffer_size + 4))

    # calculate the length of the ground_truth polygons that are not in the detector_output lines
    diff = unary_union(ground_truth).difference(unary_union(detector_output))

    return diff.length


# a function that calculates the true_positives for a given element
def calc_true_positives(element):
    ground_truth = []
    detector_output = []

    for line_element in element.iter('line'):
        points_str = line_element.get('points')
        points = parse_points(points_str)
        detector_output.append(LineString(points))

    for polygon_element in element.iter('polygon'):
        points_str = polygon_element.get('points')
        points = parse_points(points_str)
        points = np.append(points, [points[0]], axis=0)
        for point_idx, ele in np.ndenumerate(points):
            point_idx = point_idx[0]
            ground_truth.append(
                LineString([points[point_idx], points[(point_idx + 1) % len(points)]]).buffer(buffer_size + 4))

    # calculate the lenght of the detector_output lines that are in the ground_truth polygons
    intersection = unary_union(detector_output).intersection(unary_union(ground_truth))

    return intersection.length


def calc_metrics_for_all_images(xml_root, images_path):
    iou_array = []
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    for image_element in xml_root.iter('image'):
        image_name = image_element.get('name')
        image_path = images_path + image_name

        img = cv2.imread(image_path)

        if not os.path.exists(image_path):
            continue

        false_positive, iou = calc_metrics(image_element)
        iou_array.append(iou)

        false_positives += false_positive

        true_positive = calc_true_positives(image_element)
        true_positives += true_positive

        false_negative = calc_false_negatives(image_element)
        false_negatives += false_negative

    # calculate the precision
    precision = true_positives / (true_positives + false_positives)

    # calulate recall
    recall = true_positives / (true_positives + false_negatives)

    # calculate f1 score with more weight on precision
    beta = 1.3
    f1 = (1 + beta ** 2) * (precision * recall) / ((beta ** 2 * precision) + recall)

    return precision, recall, iou_array, f1
