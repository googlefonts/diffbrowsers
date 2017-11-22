import unittest
import os
from diffbrowsers.diffbrowsers import DiffBrowsers


class TestDiffBrowsers(unittest.TestCase):

    def setUp(self):
        """Monkey patch BrowserDiff __init__ method so it does not post
        fonts to GF Regression"""
        def _diffbrowsers_monkey_patch_init(self):
            self.uid = 'custom-uuid'

        TestDiffBrowsers = DiffBrowsers
        TestDiffBrowsers._post_fonts_to_test = _diffbrowsers_monkey_patch_init

        self.fonts_after = ['fonts_before.ttf']
        self.fonts_before = ['fonts_after.ttf']

        self.diffbrowsers = TestDiffBrowsers(None, './foo', self.fonts_after, self.fonts_before)

    def test_url_builder(self):
        """Test DiffBrowsers can build urls for GF Regression"""
        waterfall_url_before, waterfall_url_after = self.diffbrowsers._build_view_urls('waterfall')
        self.assertEqual('http://45.55.138.144/screenshot/custom-uuid/waterfall/before',
                         waterfall_url_before)
        self.assertEqual('http://45.55.138.144/screenshot/custom-uuid/waterfall/after',
                         waterfall_url_after)

    def test_url_builder_with_pt_size(self):
        glyphs_all_url_before, glyphs_all_url_after = self.diffbrowsers._build_view_urls('glyphs-all', pt=20)
        self.assertEqual('http://45.55.138.144/screenshot/custom-uuid/glyphs-all/after/20',
                         glyphs_all_url_after)
        self.assertEqual('http://45.55.138.144/screenshot/custom-uuid/glyphs-all/before/20',
                         glyphs_all_url_before)


if __name__ == '__main__':
    unittest.main()
