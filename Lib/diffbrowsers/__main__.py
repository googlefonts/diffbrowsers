#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Browserdiff
~~~~~~~~~~~

Compare two sets of fonts for regressions

Caveats, script is incredibly slow due to the Browserstack api. Fonts are
matched by filenames.

See README.md for further info

Basic Usage:
diffbrowsers [fonts_after] -fb [fonts_before] -o ~/Desktop/font_img_dir

Compare against family hosted on Google Fonts:
diffbrowsers [fonts_after] -gf -o ~/Desktop/font_img_dir
"""
from __future__ import print_function, division, absolute_import, unicode_literals
import argparse
import os

from diffbrowsers.diffbrowsers import DiffBrowsers
from diffbrowsers.browsers import test_browsers
from diffbrowsers.utils import load_browserstack_credentials, cli_reporter


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    
    parser.add_argument('fonts_after', nargs="+", help="Fonts after paths")
    before_group = parser.add_argument_group(title="Fonts before input")
    before_input_group = before_group.add_mutually_exclusive_group(required=True)
    before_input_group.add_argument('-fb', '--fonts-before', nargs="+",
                                  help="Fonts before paths")
    before_input_group.add_argument('-gf', '--from-googlefonts', action='store_true',
                               help="Diff against GoogleFonts instead of fonts_before")
    parser.add_argument('-o', '--output-dir', help="Directory for output images",
                        required=True)
    parser.add_argument('-pt', '--type-point-size',
                        help="In some views, users can control type sample size")
    parser.add_argument('-b', '--browsers',
                        choices=['all_browsers', 'gdi_browsers', 'android_browsers'],
                        default='all_browsers',
                        help="Which set of browsers to test on")
    parser.add_argument('-v', '--view', choices=[
                        'waterfall', 'glyphs-new', 'glyphs-modified',
                        'glyphs-missing', 'glyphs-all'], default='waterfall')
    parser.add_argument('-gif', '--output-gifs', action='store_true', default=False,
                        help="Output before and after gifs")
    args = parser.parse_args()

    auth = load_browserstack_credentials()
    browsers_to_test = test_browsers[args.browsers]

    fonts_before = 'from-googlefonts' if args.from_googlefonts \
                    else args.fonts_before

    diffbrowsers = DiffBrowsers(auth, fonts_before, args.fonts_after,
                                args.output_dir, browsers_to_test)
    diffbrowsers.diff_view(args.view, args.type_point_size, args.output_gifs)

    report_path = os.path.join(args.output_dir, 'report.txt')
    with open(report_path, 'w') as doc:
        report = cli_reporter(diffbrowsers.stats)
        doc.write(report)
        print(report)


if __name__ == '__main__':
    main()
