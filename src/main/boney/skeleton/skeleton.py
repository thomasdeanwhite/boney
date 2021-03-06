class Skeleton ():
    root_nodes = []

    def set_root_nodes(self, bones):
        self.root_nodes = bones

    def interpolate(self, skeleton, animation_progress):
        interpolated_bones = []

        # interpolate all top level bones (no parents to them)
        for f in range(len(self.root_nodes)):

            if f >= len(skeleton.root_nodes):
                break

            first_bone = self.root_nodes[f]
            second_bone = skeleton.root_nodes[f]

            interpolated_bone = first_bone.interpolate(second_bone, animation_progress)
            interpolated_bones.append(interpolated_bone)

        # new skeleton with top level bones
        skeleton = Skeleton()
        skeleton.set_root_nodes(interpolated_bones)

        return skeleton