import cv2
import numpy as np

import math
from skimage.transform import (hough_line, hough_line_peaks,
                               probabilistic_hough_line)
from skimage.feature import canny
from skimage import data, restoration
from scipy import signal

import matplotlib.pyplot as plt

grid_size = (1, 5)

img = cv2.imread("test_sequence.png")

def get_color_codes(img):
    return (img[..., 0]/32).astype(int) * 1000000 + (img[..., 1]/32).astype(int) * 1000 + (img[..., 2]/32).astype(int)

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
        if sum < threshold or unique_vals[i] == 7007007: # white color
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

                frame[str(unique_vals[v])] = [x1, y1, x2, y2]

            bones[anim].append(frame)

        bones[anim].append(bones[anim][0])
        imgs[anim].append(imgs[anim][0])

    return bones, unique_vals

def interpolate(bones, animation, progress, color_codes):
    anim = bones[animation]

    length = len(anim)

    frame_prog = progress * length

    disp = 1/length

    i1 = int(frame_prog)
    i2 = int(math.ceil(frame_prog))
    points = []

    if i1 != i2:
        anim_prog = (progress- i1*disp) / disp

        print(anim_prog)

        for c in range(len(color_codes)):
            key = str(color_codes[c])
            lines = []
            for i in range(len(anim[i1][key])):
                lines.append(int(anim[i1][key][i] * (1-anim_prog) + anim[i2][key][i] * anim_prog))

            points.append(lines)
    else:
        for c in range(len(color_codes)):
            key = str(color_codes[c])
            lines = []
            for i in range(len(anim[i1][key])):
                lines.append(int(anim[i1][key][i]))

            points.append(lines)
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
        p1 = p[0],p[1]
        p2 = p[2],p[3]
        cv2.line(im,(p1[0],p1[1]),(p2[0],p2[1]),(0,0,0),2)

    cv2.imshow('image',im)
    cv2.waitKey(0)

cv2.destroyAllWindows()