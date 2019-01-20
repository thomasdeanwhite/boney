from cv2 import cv2
import numpy as np
import math
from scipy import signal

grid_size = (1, 5)

join_threshold = 0.3

img = cv2.imread("test_sequence2.png")

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

    if lines is None:
        return 0, 0, 0, 0, im

    min_x, min_y = img_color_codes.shape[:2]
    max_x, max_y = (0, 0)

    line_count = len(lines)
    longest_line = [0, 0, 0, 0]
    line_length = 0

    for l in range(len(lines)):
        for x1,y1,x2,y2 in lines[l]:

            length = pow(x1-x2, 2) + pow(y1-y2, 2)
            if length > line_length:
                longest_line = [x1, y1, x2, y2]
                line_length = length

    return longest_line[0], longest_line[1], longest_line[2], longest_line[3], im



def gen_bones(img, grid_size):

    threshold = 0.001

    imgs = {}

    dims = img.shape[:2]

    disp = (int(dims[0]/grid_size[0]), int(dims[1]/grid_size[1]))

    area = disp[0]*disp[1]

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

                if math.pow(x1 - disp[0]/2, 2) + math.pow(y1 - disp[1]/2, 2) < math.pow(x2 - disp[0]/2, 2) + math.pow(y2 - disp[1]/2, 2):
                    x1, x2, y1, y2 = (x2, x1, y2, y1)

                frame[str(unique_vals[v])]  = [x1, y1, x2, y2]

            root_nodes = {}
            for v in range(len(unique_vals)):
                key = str(unique_vals[v])

                if not key in frame:
                    continue

                for v2 in range(len(unique_vals)):
                    key2 = str(unique_vals[v2])

                    if not key2 in frame:
                        continue

                    n1 = frame[key]

                    # if n1[2] - disp[0] < n1[0] - disp[0] or (n1[2] == n1[0] and n1[3] - disp[1] < n1[1] - disp):
                    #     n1[0], n1[1], n1[2], n1[3] = n1[2], n1[3], n1[0], n1[1]

                    n2 = frame[key2]
                    node1 = None
                    node2 = None

                    if key in root_nodes:
                        node1 = root_nodes[key]
                    else:
                        x1, y1, x2, y2 = n1
                        node1 = [None, x1, y1, x2, y2, (math.pow(x1-x2,2)+math.pow(y1-y2,2)), []]
                        root_nodes[key] = node1

                    if key2 in root_nodes:
                        node2 = root_nodes[key2]
                    else:
                        x1, y1, x2, y2 = n2
                        node2 = [None, x1, y1, x2, y2, (math.pow(x1-x2,2)+math.pow(y1-y2,2)), []]
                        root_nodes[key2] = node2

                    if v < v2 :
                        if (math.pow(n1[0] - n2[0], 2) + math.pow(n1[1] - n2[1], 2))/area < join_threshold:
                            node1[6].append(node2)
                            node2[0] = node1

                        elif math.pow(n1[0] - n2[2], 2) + math.pow(n1[1] - n2[3], 2)/area < join_threshold:
                            node2[1], node2[2], node2[3], node2[4] = node2[3], node2[4], node2[1], node2[2]

                            node1[6].append(node2)
                            node2[0] = node1

                        elif math.pow(n1[2] - n2[2], 2) + math.pow(n1[3] - n2[3], 2)/area < join_threshold:
                            node2[1], node2[2], node2[3], node2[4] = node2[3], node2[4], node2[1], node2[2]

                            node1[6].append(node2)
                            node2[0] = node1

                        elif math.pow(n1[2] - n2[0], 2) + math.pow(n1[3] - n2[0], 2)/area < join_threshold:
                            node1[6].append(node2)
                            node2[0] = node1

            removals = []

            for n_key in root_nodes.keys():
                n = root_nodes[n_key]
                if n[0] != None:
                    #
                    # dx, dy = (n[1] - n[3]), (n[2]-n[4])
                    #
                    # n1 = n[1:5]
                    # n2 = n[0][1:5]
                    #
                    # if (math.pow(n1[0] - n2[0], 2) + math.pow(n1[1] - n2[1], 2))/area < join_threshold:
                    #     n[1], n[2] = n[0][1], n[0][2]
                    # elif math.pow(n1[0] - n2[2], 2) + math.pow(n1[1] - n2[3], 2)/area < join_threshold:
                    #     n[1], n[2] = n[0][3], n[0][4]
                    #
                    # n[3], n[4] = n[1] + dx, n[2] + dy

                    removals.append(n_key)

            # for removal in removals:
            #     root_nodes.pop(removal)

            root_nodes_list = []

            for rn in root_nodes.values():
                root_nodes_list.append(rn)

            bones[anim].append(root_nodes_list)
            imgs[anim].append(imgs[anim][0])

    return bones, unique_vals
dims = img.shape[:2]

size = (int(dims[0]/grid_size[0]), int(dims[1]/grid_size[1]))

def interpolate(bones, animation, progress, color_codes):
    global disp
    progress = progress - int(progress)

    anim = bones[animation]

    length = len(anim)

    frame_prog = progress * length
    area = size[0]*size[1]
    disp = 1/length

    i1 = int(frame_prog)
    i2 = int(math.ceil(frame_prog)) % length
    points = []

    nodes = []

    nodes.append([anim[i1], anim[i2]])

    anim_prog = (progress- i1*disp) / disp

    while len(nodes) > 0:
        node = nodes.pop(0)
        if node is None:
            continue

        f1 = node[0]
        f2 = node[1]
        for f in range(len(f1)):

            frame1 = f1[f]
            frame2 = f2[f]

            # if frame1[0] != None:
            #     n = frame1
            #     dx, dy = (n[1] - n[3]), (n[2]-n[4])
            #     n1 = n[1:5]
            #     n2 = n[0][1:5]
            #
            #     if (math.pow(n1[0] - n2[0], 2) + math.pow(n1[1] - n2[1], 2))/area < join_threshold:
            #         n[1], n[2] = n[0][1], n[0][2]
            #     elif math.pow(n1[0] - n2[2], 2) + math.pow(n1[1] - n2[3], 2)/area < join_threshold:
            #         n[1], n[2] = n[0][3], n[0][4]
            #
            #     n[3], n[4] = n[1] + dx, n[2] + dy
            # if frame2[0] != None:
            #     n = frame2
            #     dx, dy = (n[1] - n[3]), (n[2]-n[4])
            #
            #     n1 = n[1:5]
            #     n2 = n[0][1:5]
            #
            #     if (math.pow(n1[0] - n2[0], 2) + math.pow(n1[1] - n2[1], 2))/area < join_threshold:
            #         n[1], n[2] = n[0][1], n[0][2]
            #     elif math.pow(n1[0] - n2[2], 2) + math.pow(n1[1] - n2[3], 2)/area < join_threshold:
            #         n[1], n[2] = n[0][3], n[0][4]
            #
            #     n[3], n[4] = n[1] + dx, n[2] + dy

            lines = []

            for i in range(4):
                lines.append(int(frame1[i+1] * (1-anim_prog) + frame2[i+1] * anim_prog))

            points.append(lines)

            # for n in range(len(frame1[6])):
            #     if len(frame2[6]) <= n:
            #         break
            #     nodes.append([frame1[6][n], frame2[6][n]])

    return points

bones, cols = gen_bones(img, grid_size)



frs = 24

for i in range(frs):
    progress = i/frs
    points = interpolate(bones, "spin", progress, cols)
    im = np.zeros([size[0], size[1]])  + 255
    for pi in range(len(points)):
        p = points[pi]
        p1 = int(p[0]),int(p[1])
        p2 = int(p[2]),int(p[3])
        cv2.line(im,(p1[0],p1[1]),(p2[0],p2[1]),(0,0,0),2)
    cv2.imwrite('imgs/' + str(i) + '.png',im)

    cv2.imshow('image',im)
    cv2.waitKey(100)

cv2.destroyAllWindows()