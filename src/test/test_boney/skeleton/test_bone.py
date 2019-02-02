import unittest


from boney.skeleton.joint import Joint
from boney.skeleton.bone import Bone

class TestBoneMethods(unittest.TestCase):

    def test_length(self):
        bone = Bone(Joint(0, 0), Joint(0, 1), "b1")

        self.assertAlmostEqual(1, bone.get_length())

    def test_add_child_root_joint(self):
        bone = Bone(Joint(0, 0), Joint(0, 1), "b1")

        bone2 = Bone(Joint(0, 0), Joint(1, 0), "b1")

        bone.add_child(bone2)

        bone.normalize_children()

        self.assertAlmostEqual(0, bone.children[0].root_joint.x)
        self.assertAlmostEqual(1, bone.children[0].root_joint.y)


    def test_add_child_direction(self):
        bone = Bone(Joint(0, 0), Joint(0, 1), "b1")

        bone2 = Bone(Joint(0, 0), Joint(1, 0), "b1")

        bone.add_child(bone2)

        bone.normalize_children()

        self.assertAlmostEqual(1, bone.children[0].next_joint.x)
        self.assertAlmostEqual(0, bone.children[0].next_joint.y)

if __name__ == '__main__':
    unittest.main()