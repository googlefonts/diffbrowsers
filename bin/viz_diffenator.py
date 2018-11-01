"""
Visualize any differences found with fontdiffenator
"""
import argparse
from diffbrowsers.gfregression import GF_PRODUCTION_URL, VIEWS
from diffbrowsers.diffbrowsers import DiffBrowsers
from diffbrowsers.browsers import test_browsers
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fonts_a', nargs="+", required=True)
    parser.add_argument('--fonts_b', nargs="+", required=True)
    parser.add_argument('-u', '--gfr-url', default=GF_PRODUCTION_URL,
                        help="Url to GFR instance")
    parser.add_argument('-l', '--gfr-local', action="store_true", default=False)
    args = parser.parse_args()

    browsers_to_test = test_browsers['safari_latest']
    output_dir = 'out'
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    font_img_dir = os.path.join(output_dir, os.path.basename(args.fonts_a)[:-4])

    diffbrowsers = DiffBrowsers(gfr_instance_url=args.gfr_url,
                                gfr_is_local=args.gfr_local,
                                dst_dir=font_img_dir,
                                browsers=browsers_to_test)

    diffbrowsers.new_session(args.fonts_a, args.fonts_b)

    views_to_diff = diffbrowsers.gf_regression.info['diffs']
    logger.info("Following diffs have been found [%s]. Genning images." % ', '.join(views_to_diff))
    for view in views_to_diff:
        logger.info("Generating images for {}".format(view))
        if view not in VIEWS:
            logger.info("Skipping view {}".format(view))
        else:
            diffbrowsers.diff_view(view, pt=32)

    logger.info("Images saved to {}".format(output_dir))


if __name__ == '__main__':
    main()
