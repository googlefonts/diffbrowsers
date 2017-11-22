"""
If a family has been hinted with ttfautohint. The x-height must remain
the same as before. Users do notice changes:

https://github.com/google/fonts/issues/644
https://github.com/google/fonts/issues/528
"""
from __future__ import print_function, division, absolute_import, unicode_literals
import argparse
import os
import time
import logging
from diffbrowsers.diffbrowsers import DiffBrowsers
from diffbrowsers.utils import load_browserstack_credentials, cli_reporter
from diffbrowsers.browsers import test_browsers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    
    parser.add_argument('fonts_after', nargs="+", help="Fonts after paths")
    set2_group = parser.add_argument_group(title="Font set input")
    set2_input_group = set2_group.add_mutually_exclusive_group(required=True)
    set2_input_group.add_argument('-fb', '--fonts-before', nargs="+",
                                  help="Font set2 paths")
    set2_input_group.add_argument('-gf', '--from-googlefonts', action='store_true',
                               help="Diff against GoogleFonts instead of font_set2")
    parser.add_argument('-o', '--output-dir', help="Directory for output images",
                        required=True)

    args = parser.parse_args()
    auth = load_browserstack_credentials()

    browsers = test_browsers['all_browsers']

    if args.from_googlefonts:
        fonts_before = 'from-googlefonts'
    else:
        fonts_before = args.fonts_before

    diffbrowsers = DiffBrowsers(auth, args.output_dir, args.fonts_after, fonts_before,
                                browsers)

    waterfall = diffbrowsers.diff_view('waterfall', gen_gifs=True)
    logger.info("Sleeping for 10 secs. Giving Browserstack api a rest")
    time.sleep(10)

    diffbrowsers.browsers = test_browsers['osx_browser']
    diff_glyphs = diffbrowsers.diff_view('glyphs-modified', gen_gifs=True)

    report = cli_reporter(diffbrowsers.report)
    report_path = os.path.join(args.output_dir, 'report.txt')
    with open(report_path, 'w') as doc:
        doc.write(report)

    print(report)


if __name__ == '__main__':
    main()
