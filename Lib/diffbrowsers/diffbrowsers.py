from PIL import Image, ImageChops
import browserstack_screenshots
import requests
import os
from glob import glob
from ntpath import basename
import json
import time
import shutil
import logging

from browsers import test_browsers


VIEWS = [
    'glyphs-all',
    'glyphs-missing',
    'glyphs-new',
    'glyphs-modified',
    'waterfall',
]


URL_GF_REGRESSION = 'http://45.55.138.144'


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnknownGFRegressionViewError(Exception):
    def __init__(self):
        super(UnknownGFRegressionViewError, self).__init__(
        'View is not valid. Choose from [%s]' % ', '.join(VIEWS)
    )

class DiffBrowsers(object):
    """Class to control GF Regression and Browser Stack api"""
    def __init__(self, auth, dst_dir, fonts_after, fonts_before,
                 browsers=test_browsers['all_browsers']):
        self.auth = auth
        self.views = set()
        self.fonts_before = fonts_before
        self.fonts_after = fonts_after

        self.dst_dir = dst_dir
        self.uid = None   
        self.browsers = browsers
        self.report = {'views': {},
                       'fonts': map(os.path.basename, self.fonts_after)}

        self._mkdir(self.dst_dir)
        self._post_fonts_to_test()

    def diff_view(self, view, pt=None, gen_gifs=False):
        """Diff a GF Regression view"""
        logger.info('Generating diff images for view %s' % view)
        fonts_before_url, fonts_after_url = self._build_view_urls(view, pt)

        view_dir = '%s_%spt' % (view, pt) if pt else view
        view_path = os.path.join(self.dst_dir, view_dir)
        self._mkdir(view_path, overwrite=True)

        fonts_before_path = os.path.join(view_path, 'fonts_before')
        self._mkdir(fonts_before_path, overwrite=True)
        self._generate_images(fonts_before_url, fonts_before_path)

        fonts_after_path = os.path.join(view_path, 'fonts_after')
        self._mkdir(fonts_after_path, overwrite=True)
        self._generate_images(fonts_after_url, fonts_after_path)

        if gen_gifs:
            gif_dir = os.path.join(view_path, 'gifs')
            self._mkdir(gif_dir, overwrite=True)
            self._gen_gifs(fonts_before_path, fonts_after_path, gif_dir)

        diff_dir = os.path.join(view_path, 'diff')
        self._mkdir(diff_dir, overwrite=True)
        comparison = self._compare_images(fonts_before_path, fonts_after_path, diff_dir)
        self.report['views'][view] = comparison
        return comparison

    def _post_fonts_to_test(self):
        """Post fonts using the GF Regression api.

        If test_against_gf is True. font_set_2 is ignored and the fonts
        are downloaded from Google Fonts instead."""
        logger.info("Posting fonts to GF Regression")
        if self.fonts_before == 'from-googlefonts':
            url_upload = URL_GF_REGRESSION + '/api/upload/googlefonts'
            payload = [('fonts_after', open(f, 'rb')) for f in self.fonts_after]
        else:
            url_upload = URL_GF_REGRESSION + '/api/upload/user'
            payload = [('fonts_after', open(f, 'rb')) for f in self.fonts_after] + \
                      [('fonts_before', open(f, 'rb')) for f in self.fonts_before]
        request = requests.post(url_upload, files=payload)
        request_json = json.loads(request.content)
        self.uid = request_json['uid']
        logger.info("Fonts have been uploaded, uuid: %s" % self.uid)

    def _build_view_urls(self, view, pt=None):
        """Get the before_fonts and after_fonts urls for browserstack to use."""
        if view not in VIEWS:
            raise UnknownGFRegressionViewError()
        basefonts_url = '%s/screenshot/%s/%s/before' % (
            URL_GF_REGRESSION, self.uid, view)
        targetfonts_url = '%s/screenshot/%s/%s/after' % (
            URL_GF_REGRESSION, self.uid, view)

        if pt:
            basefonts_url = basefonts_url + '/%s' % pt
            targetfonts_url = targetfonts_url + '/%s' % pt
        return basefonts_url, targetfonts_url

    def _mkdir(self, path, overwrite=False):
        """Create a directory, if overwrite enabled rm -rf the dir"""
        if not os.path.isdir(path):
            os.mkdir(path)
        if overwrite:
            shutil.rmtree(path)
            os.mkdir(path)

    def _generate_images(self, url, dst_dir):
        """Generate screenshots from a url using BrowserStack"""
        config = self.browsers
        config['url'] = url

        logger.info('Sending GFR url to BrowserStack')
        bstack = browserstack_screenshots.Screenshots(auth=self.auth, config=config)
        generate_resp_json = bstack.generate_screenshots()
        job_id = generate_resp_json['job_id']

        logger.info('Browserstack is processing: '
                    'http://www.browserstack.com/screenshots/%s' % job_id)
        screenshots_json = bstack.get_screenshots(job_id)
        while screenshots_json == False: # keep refreshing until browerstack is done
            time.sleep(3)
            screenshots_json = bstack.get_screenshots(job_id)
        for screenshot in screenshots_json['screenshots']:
            filename = self._build_filename_from_browserstack_json(screenshot)
            base_image = os.path.join(dst_dir, filename)
            self._download_file(screenshot['image_url'], base_image)

    def _build_filename_from_browserstack_json(self, j):
        """Build useful filename for an image from the screenshot json metadata"""
        filename = ''
        device = j['device'] if j['device'] else 'Desktop'
        if j['state'] == 'done' and j['image_url']:
            detail = [device, j['os'], j['os_version'],
                      j['browser'], j['browser_version'], '.jpg']
            filename = '_'.join(item.replace(" ", "_") for item in detail if item)
        else:
            logger.info('screenshot timed out, ignoring this result')
        return filename

    def _download_file(self, uri, filename):
        try:
            with open(filename, 'wb') as handle:
                request = requests.get(uri, stream=True)
                for block in request.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)
        except IOError, e:
            logger.info(e)

    def _gen_gifs(self, dir1, dir2, out_dir):
        shared_imgs = self._matched_filenames_in_dirs(dir1, dir2, 'jpg')
        for img in shared_imgs:
            gif_filename = img[:-4] + '.gif'
            dir1_img_path = os.path.join(dir1, img)
            dir2_img_path = os.path.join(dir2, img)
            dir1_img = Image.open(dir1_img_path)
            dir2_img = Image.open(dir2_img_path)

            logger.info('Generating gif: %s' % gif_filename)
            dir1_img.save(
                os.path.join(out_dir, gif_filename),
                save_all=True,
                append_images=[dir2_img],
                loop=10000,
                duration=1000
        )

    def _matched_filenames_in_dirs(self, dir1, dir2, ext):
        """find matching filenames in two different dirs which have a specific
        extension"""
        dir1_items = {basename(n): n for n in glob('%s/*.%s' % (dir1, ext))}
        dir2_items = {basename(n): n for n in glob('%s/*.%s' % (dir2, ext))}
        return set(dir1_items) & set(dir2_items)

    def _compare_images(self, dir1, dir2, diff_dir):
        """Compare two folders of images against each other."""
        comparisons = []

        shared_imgs = self._matched_filenames_in_dirs(dir1, dir2, 'jpg')
        for img in shared_imgs:
            dir1_img = os.path.join(dir1, img)
            dir2_img = os.path.join(dir2, img)
            diff_img = os.path.join(diff_dir, img)
            comparison = compare_image(Image.open(dir1_img),
                                       Image.open(dir2_img), diff_img)
            comparisons.append((img, comparison))
        return comparisons


def compare_image(img1, img2, out_img=None, ignore_first_px_rows=200):
    """Compare two images and return the amount of different pixels.

    ignore_first_px_rows param will ignore the first n pixel rows. This is
    useful if the images contain text which shouldn't be diffed and may
    change such as a header."""
    img_diff = ImageChops.difference(img1, img2)

    pixels = list(img_diff.getdata())
    width, height = img_diff.size
    pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]

    px_diff = 0
    for line in pixels[ignore_first_px_rows:]:
        for px in line:
            # ignore image alpha channel if exists
            r, g, b = px[:3]
            if r != 0 or g != 0 or b != 0:
                px_diff += 1
    if out_img:
        img_diff.save(out_img[:-4] + '.png')
    return px_diff
