# Add all images that are not in the xml file to the xml file with a label of 'empty'
# image attributes: name, label, id (continues from the last id in the xml file)

import xml.etree.ElementTree as ET
import os

# load xml file
# Path: dataset/annotations.xml
tree = ET.parse('../dataset/annotations.xml')

# get root element
root = tree.getroot()

# get the last id
last_id = 0
for img in root.iter('image'):
    if 'id' in img.attrib:
        if int(img.attrib['id']) > last_id:
            last_id = int(img.attrib['id'])

# iterate over all images
for img in os.listdir('../dataset/images'):
    # get the image name
    img_name = img

    found = False
    # iterate over all elements
    for ele in root.iter('image'):
        # check if the image name is the same
        if ele.attrib['name'] == img_name:
            found = True

    # if the image name is not found in the xml file add it
    if not found:
        last_id += 1
        new_img = ET.SubElement(root, 'image', {'name': img_name, 'label': 'empty', 'id': str(last_id)})

# save the xml file
tree.write('../dataset/annotations.xml')