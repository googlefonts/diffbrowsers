"""
Testing Roboto hinted sources from 3rd party supplier.

WARNING: Run time is astronomical.

12 sizes x 18 fonts = ~18 hours

This should only be run if the 3rd party supplier has updated
cvt, fpgm and prep tables.

Throw this onto AWS or another cloud platform.

"""
from __future__ import print_function, division, absolute_import, unicode_literals
import argparse
import requests
import json
import os
import sys
from ntpath import basename
from glob import glob
import shutil
import time
import logging

from diffbrowsers.diffbrowsers import DiffBrowsers
from diffbrowsers.utils import load_browserstack_credentials, cli_reporter
from diffbrowsers.browsers import test_browsers
from diffbrowsers.utils import download_file


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_current_hinted_fonts(dst):
    """Download the latest hinted src fonts from google/roboto/src/hinted
    """
    filepaths = []
    api_url = 'https://api.github.com/repos/google/roboto/contents/src/hinted'

    request = requests.get(api_url)
    request_json = json.loads(request.content)
    logger.info('Downloading existing hinted sources')
    for item in request_json:
        if item['download_url'].endswith('.ttf'):
            filename = basename(item['download_url'])
            filepath = os.path.join(dst, filename)
            logger.info('Downloading %s to %s' % (filename, dst))
            download_file(item['download_url'], filepath)
            filepaths.append(filepath)
    return filepaths


def main(font_before, font_after, out_dir):
    """Due to the fonts containing so many glyphs, style on style
    comparisons are needed."""
    auth = load_browserstack_credentials()
    logger.info('Comparing %s' % os.path.basename(font_before))
    fullname = font_before[:-4]
    font_dir = os.path.join(out_dir, fullname)
    diffbrowsers = DiffBrowsers(auth, font_dir,
                              [font_after],
                              [font_before],
                              test_browsers['all_browsers'])

    diffbrowsers.diff_view('waterfall', gen_gifs=True)
    logger.info('Resting Browserstack screenshot api')
    time.sleep(10)
    
    # Generate glyph plots for Material Design sp sizes
    for n in [11, 12, 13, 14, 16, 15, 20, 24, 34, 45, 56, 112]:
        diffbrowsers.diff_view('glyphs-all', pt=n, gen_gifs=True)
        logger.info('Resting Browserstack screenshot api')
        time.sleep(10)

    report = cli_reporter(diffbrowsers.report)
    report_path = os.path.join(font_dir, 'report.txt')
    with open(report_path, 'w') as doc:
        doc.write(report)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
