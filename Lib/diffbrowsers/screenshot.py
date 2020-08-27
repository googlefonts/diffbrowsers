from __future__ import division, absolute_import
import logging
import browserstack_screenshots
import os
import time
from pprint import pprint
import json
from diffbrowsers.utils import download_file


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ScreenShot(browserstack_screenshots.Screenshots):
    """Expansion for browserstack screenshots Lib. Adds ability to
    download files"""

    def _process_response(self, req):
        try:
            req.raise_for_status()
            return req
        except Exception as e:
            known_statuses = {
                401: "Authentication Failure",
                403: "Screenshot not allowed",
                422: "InvalidRequestError (Unprocessable Entity)"
            }
            print(f'Request Exception Information {req.status_code} {known_statuses.get(req.status_code, "UnexpectedError")}')
            if req.headers is not None:
                print('Response Headers:')
                for name, value in req.headers.items():
                    print(f'  {name}: {value}')

            if req.status_code == 422:
                json_content = json.loads(req.content)
                # {'message': 'Parallel limit reached', 'running_sessions': 5}
                # Retry-After: 56
                # stupid monkey patch :-D
                if json_content['message'] == 'Parallel limit reached':
                    json_content['Retry-After'] = int(req.headers['Retry-After'])
                    req.json = lambda: json_content
                    return req
            print('req.content', req.content)
            raise e

    def take(self, url, dst_dir):
        """take a screenshot from a url and save it to the dst_dir"""
        for status, min_wait_time in self.poll_screenshots(url, dst_dir):
            print(f'sleep {status} {min_wait_time}')
            time.sleep(min_wait_time)

    def poll_screenshots(self, url, dst_dir):
        """take a screenshot from a url and save it to the dst_dir"""
        self.config['url'] = url
        logger.info('Taking screenshot for url: %s' % url)

        while True:
            generate_resp_json = self.generate_screenshots()
            if 'Retry-After' not in generate_resp_json:
                break
            logger.info(f'Browserstack is busy {generate_resp_json["message"]} '
                    f' running sessions {generate_resp_json["running_sessions"]}'
                    f' retry after: {generate_resp_json["Retry-After"]} seconds')

            yield 'suspend', generate_resp_json['Retry-After']

        job_id = generate_resp_json['job_id']

        logger.info('Browserstack is processing: '
                    'http://www.browserstack.com/screenshots/%s' % job_id)

        # 5 is the default api wait_time:
        #       Required if specifying the time (in seconds) to wait
        #       before taking the screenshot.
        # Default: 5
        # Values: 2, 5, 10, 15, 20, 60]
        initial_min_wait_time = self.config.get('wait_time', 5)

        print('wait_time', initial_min_wait_time)
        print('url', self.config['url'])
        yield 'initial', initial_min_wait_time
        while True:
            screenshots_json = self.get_screenshots(job_id)
             # keep refreshing until browerstack is done
            if screenshots_json != False:
                break # received a result
            yield 'pending', 3 # sleep/repeat in caller!

        for screenshot in screenshots_json['screenshots']:
            filename = self._build_filename_from_browserstack_json(screenshot)
            base_image = os.path.join(dst_dir, filename)
            try:
                download_file(screenshot['image_url'], base_image)
            except:
                logger.info('Skipping {} BrowserStack timed out'.format(
                    screenshot['image_url'])
                )

    def _build_filename_from_browserstack_json(self, j):
        """Build useful filename for an image from the screenshot json
        metadata"""
        filename = ''
        device = j['device'] if j['device'] else 'Desktop'
        if j['state'] == 'done' and j['image_url']:
            detail = [device, j['os'], j['os_version'],
                      j['browser'], j['browser_version'], '.jpg']
            filename = '_'.join(item.replace(" ", "_") for item in detail if item)
        else:
            logger.info('screenshot timed out, ignoring this result')
        return filename
