"""
Testing Roboto hinted sources from 3rd party supplier.

WARNING: Run time is astronomical.

12 sizes x 18 fonts = ~18 hours

This should only be run if the 3rd party supplier has updated
cvt, fpgm and prep tables.

To avoid source mixups, the hinted sources are downloaded from the
github repository.

Throw this onto AWS or another cloud platform.

"""
import argparse
import requests
import json
import os
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('fonts', nargs="+",
                         help="Fonts to be tested against existing sources")
    parser.add_argument('out_dir')
    auth = load_browserstack_credentials()
    args = parser.parse_args()

    browsers = test_browsers['all_browsers']
    fonts_before_dir = os.path.join(args.out_dir, 'before_fonts')
    fonts_after_dir = os.path.join(args.out_dir, 'after_fonts')

    for path in (args.out_dir, fonts_before_dir, fonts_after_dir):
        if not os.path.isdir(path):
            os.mkdir(path)

    download_current_hinted_fonts(fonts_before_dir)
    fonts_before = {basename(f): os.path.join(fonts_before_dir, f) for f
                    in os.listdir(fonts_before_dir) if f.endswith('.ttf')}

    for font_path in args.fonts:
        logger.info('Copying %s to %s' % (font_path, fonts_after_dir))
        shutil.copy(font_path, fonts_after_dir)

    fonts_after = {basename(f): os.path.join(fonts_after_dir, f) for f
                   in os.listdir(fonts_after_dir) if f.endswith('.ttf')}

    shared_fonts = set(fonts_before.keys()) & set(fonts_after.keys())
    if not shared_fonts:
        raise Exception('Your Fonts are not Roboto. '
                        'Filenames must match hinted sources')
    # Due to the fonts containing so many glyphs, style on style comparisons
    # are needed.
    for font_path in shared_fonts:
        logger.info('Comparing %s' % font_path)
        fullname = font_path[:-4]
        font_dir = os.path.join(args.out_dir, fullname)
        diffbrowsers = DiffBrowsers(auth, font_dir,
                                  [fonts_after[font_path]],
                                  [fonts_before[font_path]],
                                  browsers)

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
    main()
