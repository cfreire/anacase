from time import sleep
import cv2
import logging
import sys

_log = logging.getLogger(__name__)


class Camera:
    """ Camera setup and motion detect """

    def __init__(self, camera_data):
        self.cam = None
        self.frame = None
        self.frame_delta = None
        self.frame_thresh = None
        self.first_frame = None
        self._gray_frame = None
        try:
            camera_id = int(camera_data['camera_id'])
            width = int(camera_data['camera_width'])
            height = int(camera_data['camera_height'])
            fps = int(camera_data['camera_fps'])
            camera_delay = int(camera_data['camera_delay'])
            self._resize_width = int(camera_data['camera_resize_width'])
            self._resize_height = int(camera_data['camera_resize_height'])
            self._min_detect_area = int(camera_data['min_detect_area'])
            self._gaussian_blur_value = int(camera_data['gaussian_blur_value'])
            self._threshold_value = int(camera_data['threshold_value'])
            _log.info('starting v4l on camera id "{}"'.format(camera_id))
        except ValueError as ex:
            msg = 'error reading camera_data {}. Aborting!'.format(ex)
            _log.error(msg)
            sys.exit(msg)
        try:
            self._cam = cv2.VideoCapture(camera_id)
            self._cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self._cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self._cam.set(cv2.CAP_PROP_FPS, fps)
            _log.debug('resize camera sensor to {}x{}'.format(width, height))
            sleep(camera_delay)
            (grabbed, frame) = self._cam.read()
            if not grabbed:  # error in camera
                msg = 'error reading frame on camera id "{}. Aborting!"'.format(camera_id)
                _log.critical(msg)
                sys.exit(msg)
        except AttributeError as ex:
            msg = 'critical setup camera id {} - {}. Aborting!'.format(camera_id, ex)
            _log.critical(msg)
            sys.exit(msg)

    def calibrate(self):
        """Get image, resize, gray, blur"""
        # get new image
        (grabbed, self.frame) = self._cam.read()
        # test reading camera
        if not grabbed:
            _log.critical('error reading frame from camera')
            sys.exit('abnormal program termination!')
        self.frame = cv2.resize(self.frame, (self._resize_width, self._resize_height))
        self._gray_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        self._gray_frame = cv2.GaussianBlur(self._gray_frame, (self._gaussian_blur_value, self._gaussian_blur_value), 0)
        if self.first_frame is None:
            self.first_frame = self._gray_frame

    @property
    def objects(self):
        """ Compute the absolute difference between the current frame and first frame and find contours """
        self.calibrate()
        self.frame_delta = cv2.absdiff(self.first_frame, self._gray_frame)
        self.frame_thresh = cv2.threshold(self.frame_delta, self._threshold_value, 255, cv2.THRESH_BINARY)[1]
        self.frame_thresh = cv2.dilate(self.frame_thresh, None, iterations=2)
        im2, contours, hierarchy = cv2.findContours(self.frame_thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for obj in contours:
            if cv2.contourArea(obj) > self._min_detect_area:
                yield obj

    def close(self):
        self._cam.release()
        _log.debug('closing camera')


def main():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    camera_data = {'camera_id': 0, 'camera_delay': 2, 'camera_width': 800, 'camera_height': 600,
                   'gaussian_blur_value': 21, 'min_detect_area': 3000, 'threshold_value': 60,
                   'camera_resize_width': 800, 'camera_resize_height': 480, 'camera_fps': 1}
    cam = Camera(camera_data)
    cam.calibrate()
    while True:

        for _ in cam.objects:
            pass
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):  # if the `q` key is pressed
            break
        cv2.imshow('CAMERA VIEW', cam.frame)
        cv2.imshow('CAMERA DELTA', cam.frame_delta)
        cv2.imshow('CAMERA THRESH', cam.frame_thresh)


if __name__ == '__main__':
    main()
