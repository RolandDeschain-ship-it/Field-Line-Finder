import os

import numpy as np
from PIL import Image
import xml.etree.ElementTree as ET
from shapely.geometry import Point, Polygon

from tqdm import tqdm
import cv2
import numpy as np
import xml.etree.ElementTree as ET


def extract_lines(image_dir, xml_path, output_file, horizontal_spacing, vertical_spacing):
    # Initialize lists for storing results
    horizontal_results = []
    vertical_results = []
    # Get the total number of images
    num_images = len(os.listdir(image_dir))

    # Iterate over images in the directory
    with tqdm(total=num_images, desc="Processing Images") as o_pbar:
        # Open the output file for writing
        with open(output_file, 'w') as file:
            # Get the list of image files in the directory
            image_files = os.listdir(image_dir)

            # Iterate over images in the directory
            for image_file in tqdm(image_files, desc="Processing Images"):
                image_path = os.path.join(image_dir, image_file)

                # Load the image
                image = cv2.imread(image_path)

                # Parse the XML file
                tree = ET.parse(xml_path)
                root = tree.getroot()
                # Get the image dimensions
                height, width, _ = image.shape

                # Extract the polygon points
                polygon_points = []
                image_name = image_file.split("/")[-1]  # Extract the image filename
                for image_elem in root.findall("image"):
                    if image_elem.attrib["name"] == image_name:
                        for polygon in image_elem.findall("polygon"):
                            points = polygon.attrib["points"].split(";")
                            for point in points:
                                x, y = map(float, point.split(","))
                                polygon_points.append([x, y])

                #continue if polygon points is empty
                if len(polygon_points) == 0:
                    continue
                polygon_points = np.array(polygon_points, dtype=np.int32)  # Convert points to integer values



                # Iterate over horizontal lines
                for y in tqdm(range(0, height, horizontal_spacing), desc="Horizontal Lines"):
                    line_pixels = []
                    for x in range(width):
                        if cv2.pointPolygonTest(polygon_points, (x, y), False) >= 0:
                            file.write(f"{tuple(image[y, x])} False ")
                        else:
                            file.write(f"{tuple(image[y, x])} True ")
                    file.write('\n')



                # Iterate over vertical lines
                for x in tqdm(range(0, width, vertical_spacing), desc="Vertical Lines"):
                    line_pixels = []
                    for y in range(height):
                        if cv2.pointPolygonTest(polygon_points, (x, y), False) >= 0:
                            file.write(f"{tuple(image[y, x])} False ")
                        else:
                            file.write(f"{tuple(image[y, x])} True ")
                    file.write('\n')

            o_pbar.update(1)

        return


if __name__ == '__main__':
    image_dir = 'dataset/images'
    xml_file = 'dataset/annotations.xml'
    output_file = 'output.txt'
    extract_lines(image_dir, xml_file, output_file, 10, 10)
    # print(horizontal_lines)
    # print(vertical_lines)
