import unittest
import requests
from diffbrowsers.gfregression import (
    URL_GF_REGRESSION,
    GFRegression,
)

class TestGFRegressionViews(unittest.TestCase):

    def setUp(self):
        self.gf_regression = GFRegression()
        self.gf_regression.uuid = 'custom-uuid'

    def test_is_gfregression_running(self):
        request = requests.get(URL_GF_REGRESSION)
        self.assertEqual(request.status_code, 200)

    def test_url_builder(self):
        """Test DiffBrowsers can build urls for GF Regression"""
        before_url = self.gf_regression.url('waterfall', 'before')
        after_url = self.gf_regression.url('waterfall', 'after')
        self.assertEqual('http://www.gf-regression.com/screenshot/custom-uuid/waterfall/after',
                         after_url)
        self.assertEqual('http://www.gf-regression.com/screenshot/custom-uuid/waterfall/before',
                         before_url)

    def test_url_builder_with_pt_size(self):
        before_url = self.gf_regression.url('glyphs-all', 'before', pt=20)
        after_url = self.gf_regression.url('glyphs-all', 'after', pt=20)
        self.assertEqual('http://www.gf-regression.com/screenshot/custom-uuid/glyphs-all/after/20',
                         after_url)
        self.assertEqual('http://www.gf-regression.com/screenshot/custom-uuid/glyphs-all/before/20',
                         before_url)


if __name__ == '__main__':
    unittest.main()
