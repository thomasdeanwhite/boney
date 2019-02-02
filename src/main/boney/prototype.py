from cv2 import cv2
import numpy as np
import math
import sys
import getopt
from validate import image_validator, number_validator
from scipy import signal
from src.main.boney.skeleton.skeleton import Skeleton
from src.main.boney.skeleton import Bone
from src.main.boney.skeleton.joint import Joint

# Command Line parameter loading
try:
    opts, args = getopt.getopt(sys.argv[1:], "y:x:i:s:", ["ysize", "xsize", "image=", "speed="])
except getopt.GetoptError as err:
    print(err)
    sys.exit(2)

grid_size_y = None
grid_size_x = None
image_file = None
speed = None
for o, a in opts:
    if o == "-y":
        grid_size_y = a
    elif o == "-x":
        grid_size_x = a
    elif o in ("-i", "--image"):
        image_file = a
    elif o in ("-s", "--speed"):
        speed = a

grid_size_y = (number_validator.validate(grid_size_y, "Grid Height"))
grid_size_x = (number_validator.validate(grid_size_x, "Grid Width"))
image_file = image_validator.validate(image_file)
speed = 100 if speed is None else (101 - int(speed))
# End parameter loading

grid_size = (grid_size_y, grid_size_x)
join_threshold = 15
img = cv2.imread(image_file)

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
    dims = img.shape[:2]

    disp = (int(dims[0]/grid_size[0]), int(dims[1]/grid_size[1]))

    area = disp[0]*disp[1]

    col_codes = get_color_codes(img)

    unique_vals = np.unique(col_codes).tolist()

    i = 0

    color_quantity_threshold = dims[0] * dims[1] * 0.001

    while i < len(unique_vals):
        sum = np.sum(np.equal(col_codes, unique_vals[i]).astype(int))
        if sum < color_quantity_threshold or unique_vals[i] == 777: # white color
            unique_vals.pop(i)
        else:
            i += 1

    animations = {}

    anim = "spin"

    for j in range(grid_size[0]):

        animations[anim] = []
        for i in range(grid_size[1]):

            skeleton = Skeleton()

            cropped_codes = col_codes[j*disp[1]:(j+1)*disp[1], i*disp[0]:(i+1)*disp[0]]
            bones = {}

            for v in range(len(unique_vals)):

                x1, y1, x2, y2, edge = detect_line(cropped_codes, unique_vals[v])

                if math.pow(x1 - disp[0]/2, 2) + math.pow(y1 - disp[1]/2, 2) > math.pow(x2 - disp[0]/2, 2) + math.pow(y2 - disp[1]/2, 2):
                    x1, x2, y1, y2 = (x2, x1, y2, y1)

                bones[str(unique_vals[v])] = Bone(Joint(x1, y1), Joint(x2, y2), unique_vals[v])

            for v in range(len(unique_vals)):
                key = str(unique_vals[v])

                if not key in bones:
                    continue

                for v2 in range(len(unique_vals)):
                    key2 = str(unique_vals[v2])

                    if not key2 in bones or unique_vals[v] >= unique_vals[v2]:
                        continue

                    p_bone = bones[key] # possible parent bone
                    c_bone = bones[key2] # possible child bone

                    if not c_bone.parent is None:
                        continue

                    if p_bone.next_joint.snap(c_bone.root_joint, join_threshold):
                        p_bone.add_child(c_bone)

                    elif p_bone.next_joint.snap(c_bone.next_joint, join_threshold):
                        c_bone.flip()
                        p_bone.add_child(c_bone)

            removals = []

            for n_key in bones.keys():
                n = bones[n_key]
                if n.parent != None:
                    removals.append(n_key)

            for removal in removals:
                bones.pop(removal)

            bones_list = []

            for b in bones.values():
                b.normalize_children()
                bones_list.append(b)

            skeleton.set_root_nodes(bones_list)
            animations[anim].append(skeleton)

    return animations, unique_vals

dims = img.shape[:2]

size = (int(dims[0]/grid_size[0]), int(dims[1]/grid_size[1]))

def interpolate(animation, progress, color_codes):
    global disp
    progress = progress - int(progress)

    length = len(animation)

    frame_prog = progress * length

    disp = 1/length

    first_frame_index = int(frame_prog)
    second_frame_index = int(math.ceil(frame_prog)) % length

    first_frame, second_frame = animation[first_frame_index], animation[second_frame_index]

    animation_progress = (progress- first_frame_index*disp) / disp

    first_skeleton = first_frame
    second_skeleton = second_frame

    return first_skeleton.interpolate(second_skeleton, animation_progress)

animations, cols = gen_bones(img, grid_size)

frs = 100

for i in range(frs):
    progress = i/frs
    interpolated_skeleton = interpolate(animations["spin"], progress, cols)
    im = np.zeros([size[0], size[1]])  + 255
    for root_bone in interpolated_skeleton.root_nodes:

        bones = root_bone.flatten()


        for pi in range(len(bones)):
            p = bones[pi]
            p1 = int(p.root_joint.x),int(p.root_joint.y)
            p2 = int(p.next_joint.x),int(p.next_joint.y)
            cv2.line(im,(p1[0],p1[1]),(p2[0],p2[1]),(0,0,0),2)
    cv2.imwrite('imgs/' + str(i) + '.png',im)

    cv2.imshow('image', im)
    cv2.waitKey(speed)

cv2.destroyAllWindows()