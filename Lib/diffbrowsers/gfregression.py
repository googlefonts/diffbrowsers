from __future__ import division, absolute_import
import logging
import requests
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

URL_GF_REGRESSION = 'http://www.gf-regression.com'

VIEWS = [
    'glyphs-all',
    'glyphs-missing',
    'glyphs-new',
    'glyphs-modified',
    'waterfall',
]

class UnknownGFRegressionViewError(Exception):
    def __init__(self):
        super(UnknownGFRegressionViewError, self).__init__(
        'View is not valid. Choose from [%s]' % ', '.join(VIEWS)
    )

class GFRegression:
    """Simple client for GF Regression"""
    def __init__(self, uuid=None):
        self.uuid = uuid

    def upload_fonts(self, fonts_before, fonts_after):
        """Post fonts to GF Regression site using the api.

        If fonts_before == 'from-googlefonts', compare against fonts hosted
        on Google Fonts.

        If the fonts uploaded successfully, GF Regression will return a uuid.
        This can be used to form urls to view endpoints."""
        logger.info("Posting fonts to GF Regression")
        if fonts_before == 'from-googlefonts':
            url_upload = URL_GF_REGRESSION + '/api/upload/googlefonts'
            payload = [('fonts_after', open(f, 'rb')) for f in fonts_after]
        else:
            url_upload = URL_GF_REGRESSION + '/api/upload/user'
            payload = [('fonts_after', open(f, 'rb')) for f in fonts_after] + \
                      [('fonts_before', open(f, 'rb')) for f in fonts_before]
        request = requests.post(url_upload, files=payload)
        request_json = json.loads(request.content)
        self.uuid = request_json['uid']
        logger.info("Fonts have been uploaded, uuid: %s" % self.uuid)

    def url(self, view, font_type, pt=None):
        """Return a url from a user's input params."""
        if view not in VIEWS:
            raise UnknownGFRegressionViewError()
        if not self.uuid:
            raise Exception('No fonts uploaded or previous uuid defined')
        url = '%s/screenshot/%s/%s/%s' % (URL_GF_REGRESSION,
                                          self.uuid, view, font_type)
        if pt:
            url = url + '/%s' % pt
        return url
