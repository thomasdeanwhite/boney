import math

class Joint ():
    x, y = 0, 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, joint):
        diff = self - joint
        return math.sqrt(diff.x*diff.x + diff.y*diff.y)

    def snap(self, joint, threshold):
        # returns true if self and joint are can be snapped together with param threshold
        return self.distance(joint) < threshold

    def interpolate(self, joint, progress):
        return self + (joint - self).scale(progress)

    # maths point operators
    def scale(self, s):
        return Joint(self.x * float(s), self.y * float(s))

    def subtract(self, joint):
        return Joint(self.x - joint.x, self.y - joint.y)

    def add(self, joint):
        return Joint(self.x + joint.x, self.y + joint.y)

    # overwrite python's methods for + and -
    def __radd__(self, other):
        return self.add(other)
    def __add__(self, other):
        return self.add(other)
    def __sub__(self, other):
        return self.subtract(other)
    def __rsub__(self, other):
        return self.subtract(other)
