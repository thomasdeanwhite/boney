from skeleton.joint import Joint

class Bone ():
    root_joint = None
    next_joint = None
    key = None
    children = []
    length = 0
    parent = None

    def __init__(self, root_joint, next_joint, key):
        self.root_joint = root_joint
        self.next_joint = next_joint
        self.key = key
        self.children = []
        self.length = 0
        self.parent = None

    def calculate_length (self):
        self.length = self.root_joint.distance(self.next_joint)

    def flip(self):
        self.root_joint, self.next_joint = self.next_joint, self.root_joint


    def add_child(self, bone):
        self.children.append(bone)
        bone.parent = self

    def normalize_children(self):
        for c in self.children:
            displacement = c.next_joint - c.root_joint

            c.root_joint = self.next_joint

            c.next_joint = c.root_joint + displacement

            c.normalize_children()

    def interpolate(self, bone, progress):

        children = []

        for c in self.children:
            for c2 in bone.children:
                if c.key == c2.key:
                    children.append(c.interpolate(c2, progress))

        root_joint = self.root_joint.interpolate(bone.root_joint, progress)
        next_joint = self.next_joint.interpolate(bone.next_joint, progress)

        interpolated_bone = Bone(root_joint, next_joint, self.key)

        for c in children:
            interpolated_bone.add_child(c)

        interpolated_bone.normalize_children()

        return interpolated_bone

    def flatten(self): # flattens tree to a single list
        bones = [self]
        for c in self.children:
            bones += c.flatten()
        return bones