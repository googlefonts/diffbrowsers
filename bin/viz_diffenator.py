"""
Visualize any differences found with fontdiffenator
"""
import argparse
from diffenator.font import InputFont
from diffenator.diff import diff_fonts
from diffbrowsers.gfregression import GF_PRODUCTION_URL, VIEWS 
from diffbrowsers.diffbrowsers import DiffBrowsers
from diffbrowsers.browsers import test_browsers
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('font_a')
    parser.add_argument('font_b')
    parser.add_argument('-u', '--gfr-url', default=GF_PRODUCTION_URL,
                        help="Url to GFR instance")
    parser.add_argument('-l', '--gfr-local', action="store_true", default=False)
    args = parser.parse_args()

    if os.path.basename(args.font_a) != os.path.basename(args.font_b):
        raise Exception('font_a and font_b must has same filename')

    logger.info("Diffenating fonts")
    font_a = InputFont(args.font_a)
    font_b = InputFont(args.font_b)
    diff = diff_fonts(font_a, font_b)

    views_to_diff = []
    for cat in diff:
        for sub_cat in diff[cat]:
            gfr_view = '{}_{}'.format(cat, sub_cat)
            if len(diff[cat][sub_cat]) > 0 and gfr_view in VIEWS:
                views_to_diff.append(gfr_view)

    browsers_to_test = test_browsers['gdi_browsers']
    output_dir = 'out'
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    font_img_dir = os.path.join(output_dir, os.path.basename(args.font_a)[:-4])

    diffbrowsers = DiffBrowsers(gfr_instance_url=args.gfr_url,
                                gfr_is_local=args.gfr_local,
                                dst_dir=font_img_dir,
                                browsers=browsers_to_test)

    diffbrowsers.new_session([args.font_a], [args.font_b])

    for view in views_to_diff:
        logger.info("Generating images for {}".format(view))
        diffbrowsers.diff_view(view)

    logger.info("Images saved to {}".format(output_dir))


if __name__ == '__main__':
    main()
