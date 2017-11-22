import os
import unittest
from PIL import Image
from diffbrowsers.diffbrowsers import compare_image

class TestImgDiff(unittest.TestCase):

    def setUp(self):

        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.img_before_path = os.path.join(data_dir, 'img_before.jpg')
        self.img_after_path = os.path.join(data_dir, 'img_after.jpg')
        self.img_before = Image.open(self.img_before_path)
        self.img_after = Image.open(self.img_after_path)

    def test_compare_image_are_different(self):
        px_diff = compare_image(self.img_before, self.img_after)
        self.assertNotEqual(0, px_diff)

    def test_compare_image_are_same(self):
        px_diff = compare_image(self.img_before, self.img_before)
        self.assertEqual(0, px_diff)

    def test_compare_image_ignore_first_px_rows(self):
        px_diff1 = compare_image(self.img_before, self.img_after)
        px_diff2 = compare_image(self.img_before, self.img_after, ignore_first_px_rows=None)
        self.assertNotEqual(px_diff1, px_diff2)


if __name__ == '__main__':
    unittest.main()
