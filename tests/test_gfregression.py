import unittest
import requests
from diffbrowsers.gfregression import (
    GF_PRODUCTION_URL,
    GFRegression,
)
import uuid


class TestGFRegressionViews(unittest.TestCase):

    def setUp(self):
        self.gf_regression = GFRegression()
        self.uuid = str(uuid.uuid4())
        self.gf_regression.uuid = self.uuid

    def test_is_gfregression_running(self):
        request = requests.get(GF_PRODUCTION_URL)
        self.assertEqual(request.status_code, 200)

    def test_url_builder(self):
        """Test DiffBrowsers can build urls for GF Regression"""
        before_url = self.gf_regression.url('waterfall', 'before')
        after_url = self.gf_regression.url('waterfall', 'after')
        self.assertEqual('http://www.gf-regression.com/screenshot/%s/waterfall/after' % self.uuid,
                         after_url)
        self.assertEqual('http://www.gf-regression.com/screenshot/%s/waterfall/before' % self.uuid,
                         before_url)

    def test_url_builder_with_pt_size(self):
        before_url = self.gf_regression.url('glyphs-all', 'before', pt=20)
        after_url = self.gf_regression.url('glyphs-all', 'after', pt=20)
        self.assertEqual('http://www.gf-regression.com/screenshot/%s/glyphs-all/after/20' % self.uuid,
                         after_url)
        self.assertEqual('http://www.gf-regression.com/screenshot/%s/glyphs-all/before/20' % self.uuid,
                         before_url)

    def test_extract_uuid_from_url(self):
        url = 'http://www.gf-regression.com/screenshot/%s/waterfall/after' % self.uuid
        self.assertEqual(self.uuid, self.gf_regression._extract_uuid(url))

        url = 'http://www.gf-regression.com/comapre/%s' % self.uuid
        self.assertEqual(self.uuid, self.gf_regression._extract_uuid(url))


if __name__ == '__main__':
    unittest.main()
