import cv2
import numpy as np
import bezier
import math
from skimage.transform import (hough_line, hough_line_peaks,
                               probabilistic_hough_line)
from skimage.feature import canny
from skimage import data, restoration
from scipy import signal

import matplotlib.pyplot as plt

grid_size = (1, 5)

join_threshold = 0.1

img = cv2.imread("test_sequence.png")

def get_color_codes(img):
    return (img[..., 0]/32).astype(int) * 100 + (img[..., 1]/32).astype(int) * 10 + (img[..., 2]/32).astype(int)

def detect_line(img_color_codes, value):
    true_vals = np.equal(img_color_codes, value).astype(int)
    im = np.zeros_like(img_color_codes)
    im = im + (true_vals*255)

    im = signal.medfilt(im, kernel_size=[3, 3])

    im = im.astype(np.uint8)

    #im = cv2.Canny(im,100,200,apertureSize = 3)

    lines = cv2.HoughLinesP(im,1,np.pi/180, 10, 1, 10)

    min_x, min_y = img_color_codes.shape[:2]
    max_x, max_y = (0, 0)

    line_count = len(lines)

    print(line_count)

    longest_line = [0, 0, 0, 0]
    line_length = 0

    for l in range(len(lines)):
        for x1,y1,x2,y2 in lines[l]:

            length = pow(x1-x2, 2) + pow(y1-y2, 2)
            if length > line_length:
                longest_line = [x1, y1, x2, y2]
                line_length = length

    return longest_line[0], longest_line[1], longest_line[2], longest_line[3], im

    return 0, 0, 0, 0, im

def gen_bones(img, grid_size):

    threshold = 0.001

    imgs = {}

    dims = img.shape[:2]

    disp = (int(dims[0]/grid_size[0]), int(dims[1]/grid_size[1]))

    col_codes = get_color_codes(img)

    unique_vals = np.unique(col_codes).tolist()

    i = 0

    threshold = dims[0] * dims[1] * threshold

    while i < len(unique_vals):
        sum = np.sum(np.equal(col_codes, unique_vals[i]).astype(int))
        if sum < threshold or unique_vals[i] == 777: # white color
            unique_vals.pop(i)
        else:
            i += 1

    bones = {}

    anim = "spin"

    for j in range(grid_size[0]):

        imgs[anim] = []

        bones[anim] = []
        for i in range(grid_size[1]):
            cropped = img[j*disp[1]:(j+1)*disp[1], i*disp[0]:(i+1)*disp[0]]
            cropped_codes = col_codes[j*disp[1]:(j+1)*disp[1], i*disp[0]:(i+1)*disp[0]]
            imgs[anim].append(cropped)
            frame = {}

            for v in range(len(unique_vals)):

                x1, y1, x2, y2, edge = detect_line(cropped_codes, unique_vals[v])

                if x1 < x2:
                    x1, x2, y1, y2 = (x2, x1, y2, y1)
                elif x1 == x2 and y1 < y2:
                    x1, x2, y1, y2 = (x2, x1, y2, y1)

                frame[str(unique_vals[v])]  = [x1, y1, x2, y2]

            frame_tree = {}
            root_nodes = {}
            for v in range(len(unique_vals)):
                key = str(unique_vals)
                for v2 in range(len(unique_vals)):
                    key2 = str(unique_vals)
                    n1 = frame[key]
                    n2 = frame[key2]
                    node1 = None
                    node2 = None

                    if key in root_nodes:
                        node1 = root_nodes[key]
                    else:
                        x1, y1, x2, y2 = node1
                        node1 = [None, x1, y1, x2, y2, (math.pow(x1-x2,2)+math.pow(y1-y2,2)), []]
                        root_nodes[key] = node1

                    if key2 in root_nodes:
                        node2 = root_nodes[key2]
                    else:
                        x1, y1, x2, y2 = node1
                        node2 = [None, x1, y1, x2, y2, (math.pow(x1-x2,2)+math.pow(y1-y2,2)), []]
                        root_nodes[key2] = node2


                    if math.pow(n1[0] - n2[0], 2) + math.pow(n1[1] - n2[1], 2) < join_threshold:
                        if v < v2 : # v is parent node
                            node1[6].append(node2)
                            node2[0] = node1
                        else:
                            node2[6].append(node1)
                            node1[0] = node2

                    elif math.pow(n1[0] - n2[3], 2) + math.pow(n1[1] - n2[4], 2) < join_threshold:
                        if v < v2 : # v is parent node
                            n2[1], n2[2], n2[3], n2[4] = n2[3], n2[4], n2[1], n2[2]
                            node1[6].append(node2)
                            node2[0] = node1
                        else:
                            n1[1], n1[2], n1[3], n1[4] = n1[3], n1[4], n1[1], n1[2]

                            node2[6].append(node1)
                            node1[0] = node2

            for n in root_nodes.keys():
                if n[0] != None:

                    dx, dy = (n[1] - n[3]), (n[2]-n[4])

                    n[1], n[2] = n[0][3], n[0][4]
                    n[3], n[4] = n[1] + dx, n[2] + dy

                    root_nodes.pop(n)









            bones[anim].append(root_nodes)

        #bones[anim].append(bones[anim][0])
            imgs[anim].append(imgs[anim][0])

    return bones, unique_vals


def interpolate(bones, animation, progress, color_codes):
    anim = bones[animation][1:5]

    length = len(anim)

    disp = 1 / length

    points = []

    for c in range(len(color_codes)):
        key = str(color_codes[c])

        i = 1 + (progress * (len(anim[key])-1))
        frame = int(i)

        low_lim = ((frame-1)*disp)

        anim_prog = (progress - low_lim) / (disp*2)

        lines = []
        curve_p1, curve_p2 = get_curve(anim[key][frame-1:frame+1])

        point = np.append(curve_p1.evaluate(progress),(curve_p2.evaluate(progress)))

        points.append(point)
    return points




bones, cols = gen_bones(img, grid_size)

dims = img.shape[:2]

disp = (int(dims[0]/grid_size[0]), int(dims[1]/grid_size[1]))

frs = 24

for i in range(frs):
    progress = i/frs
    points = interpolate(bones, "spin", progress, cols)
    im = np.zeros([disp[0], disp[1]])  + 255
    for pi in range(len(points)):
        p = points[pi]
        p1 = int(p[0]),int(p[1])
        p2 = int(p[2]),int(p[3])
        cv2.line(im,(p1[0],p1[1]),(p2[0],p2[1]),(0,0,0),2)

    cv2.imshow('image',im)
    cv2.waitKey(0)

cv2.destroyAllWindows()