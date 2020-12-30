class Bone ():
    root_joint = None
    next_joint = None
    key = None
    children = []
    __length = -1
    parent = None

    is_rigid = True

    def __init__(self, root_joint, next_joint, key):
        # reinitialize vars here, or they are static!
        self.root_joint = root_joint
        self.next_joint = next_joint
        self.key = key
        self.children = []
        self.length = 0
        self.parent = None

    def __calculate_length__(self):
        self.__length = self.root_joint.distance(self.next_joint)

    def get_length(self):
        if self.__length == -1:
            self.__calculate_length__()
        return self.__length

    def flip(self):
        # rotate bone by PI rads
        self.root_joint, self.next_joint = self.next_joint, self.root_joint

    def add_child(self, bone):
        self.children.append(bone)
        bone.parent = self

    def stretch(self, factor):
        disp = self.next_joint - self.root_joint
        self.next_joint = self.root_joint + disp.scale(factor)

    def normalize_children(self):

        #ensure children are actually attached to this bone (recursively)
        for c in self.children:

            # get line direction/magnitude
            displacement = c.next_joint - c.root_joint

            c.root_joint = self.next_joint

            # update line pos with direction/magnitude
            c.next_joint = c.root_joint + displacement

            # recursive call
            c.normalize_children()

    def interpolate(self, bone, progress):

        # interpolate self and all children with param bone.
        # both self and bone have to have same tree structure!
        # TODO: Make this tree structure independent
        children = []

        for c in self.children:
            for c2 in bone.children:
                if c.key == c2.key:
                    children.append(c.interpolate(c2, progress))

        root_joint = self.root_joint.interpolate(bone.root_joint, progress)
        next_joint = self.next_joint.interpolate(bone.next_joint, progress)

        interpolated_bone = Bone(root_joint, next_joint, self.key)

        if self.is_rigid:
            length = self.get_length() * (1-progress)
            length += bone.get_length() * (progress)

            # stretch the bone to the length of the bones either side of the keyframe
            # to keep it rigid
            interpolated_bone.stretch(length/interpolated_bone.get_length())

        for c in children:
            interpolated_bone.add_child(c)

        interpolated_bone.normalize_children()

        return interpolated_bone

    def flatten(self): # flattens tree to a single list
        bones = [self]
        for c in self.children:
            bones += c.flatten()
        return bones