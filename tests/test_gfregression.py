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
        self.gf_regression.info['uuid'] = self.uuid

    def test_is_gfregression_running(self):
        request = requests.get(GF_PRODUCTION_URL)
        self.assertEqual(request.status_code, 200)

    def test_url_builder(self):
        """Test DiffBrowsers can build urls for GF Regression"""
        before_url = self.gf_regression.url('waterfall', 'before')
        after_url = self.gf_regression.url('waterfall', 'after')
        self.assertEqual('%s/screenshot/%s/waterfall/after' % (GF_PRODUCTION_URL, self.uuid),
                         after_url)
        self.assertEqual('%s/screenshot/%s/waterfall/before' % (GF_PRODUCTION_URL, self.uuid),
                         before_url)

    def test_url_builder_with_pt_size(self):
        before_url = self.gf_regression.url('glyphs_all', 'before', pt=20)
        after_url = self.gf_regression.url('glyphs_all', 'after', pt=20)
        self.assertEqual('%s/screenshot/%s/glyphs_all/after/20' % (GF_PRODUCTION_URL, self.uuid),
                         after_url)
        self.assertEqual('%s/screenshot/%s/glyphs_all/before/20' % (GF_PRODUCTION_URL, self.uuid),
                         before_url)

    def test_url_builder_with_style_filter(self):
        before_url = self.gf_regression.url('waterfall', 'before', styles=["Regular", "Bold"])
        self.assertEqual('%s/screenshot/%s/waterfall/before?styles=Regular,Bold' % (GF_PRODUCTION_URL, self.uuid),
                         before_url)
        after_url = self.gf_regression.url('waterfall', 'after', styles=["Regular", "Bold"])
        self.assertEqual('%s/screenshot/%s/waterfall/after?styles=Regular,Bold' % (GF_PRODUCTION_URL, self.uuid),
                         after_url)

    def test_extract_uuid_from_url(self):
        url = '%s/screenshot/%s/waterfall/after' % (GF_PRODUCTION_URL, self.uuid)
        self.assertEqual(self.uuid, self.gf_regression._extract_uuid(url))

        url = '%s/compare/%s' % (GF_PRODUCTION_URL, self.uuid)
        self.assertEqual(self.uuid, self.gf_regression._extract_uuid(url))


if __name__ == '__main__':
    unittest.main()
