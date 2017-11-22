import unittest
import requests
from diffbrowsers.diffbrowsers import (
    URL_GF_REGRESSION
)

class TestGFRegressionViews(unittest.TestCase):

    def test_is_gfregression_running(self):
        request = requests.get(URL_GF_REGRESSION)
        self.assertEqual(request.status_code, 200)


if __name__ == '__main__':
    unittest.main()
