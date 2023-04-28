import xml.etree.ElementTree as ET
import os

# load xml file
# Path: dataset/annotations.xml
tree = ET.parse('../dataset/annotations.xml')

# get root element
root = tree.getroot()

# clear all data from the xml where images has no annotations

to_remove = []

# iterate over all elements
for img in root.iter('image'):

    # check if img has attribute label with the value 'empty'
    if 'label' in img.attrib and img.attrib['label'] == 'empty':
        continue

    # check if there are child elements
    if len(img) is 0:
        # add the image to the list of images to remove
        to_remove.append(img)
        continue

    # check if image exists in the images folder
    if not os.path.exists('../dataset/images/' + img.attrib['name']):
        # add the image to the list of images to remove
        to_remove.append(img)
        continue

# remove all images from the xml file
for img in to_remove:
    root.remove(img)


# delete all images from the dataset where there are no annotations
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

    # if the image name is not found in the xml file delete it
    if not found:
        os.remove('../dataset/images/' + img_name)

# save the xml file
tree.write('../dataset/annotations.xml')
