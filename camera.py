from time import sleep
import imutils
import cv2
import logging
import sys

_log = logging.getLogger(__name__)


class Camera:
    """ Camera setup and motion detect """

    def __init__(self, camera_data):
        self.frame = None
        self.first_frame = None
        self._gray_frame = None
        self.cam = None
        self._contours = None
        try:
            self._camera_id = int(camera_data['camera_id'])
            self._width = int(camera_data['camera_width'])
            self._height = int(camera_data['camera_height'])
            self._min_detect_area = int(camera_data['min_detect_area'])
            self._gaussian_blur_value = int(camera_data['gaussian_blur_value'])
            self._threshold_value = int(camera_data['threshold_value'])
            self._camera_delay = int(camera_data['camera_delay'])
            
            _log.info('starting v4l on camera id "{}"'.format(self._camera_id))
        except ValueError as ex:
            msg = 'error reading camera_data {}. Aborting!'.format(ex)
            _log.error(msg)
            sys.exit(msg)
        try:
            self._cam = cv2.VideoCapture(self._camera_id)
            self._cam.set(3, self._width) 
            self._cam.set(4, self._height)
            sleep(self._camera_delay)
            (grabbed, self.frame) = self._cam.read()
            if not grabbed:  # error in camera
                msg = 'error reading frame on camera id "{}. Aborting!"'.format(self._camera_id)
                _log.critical(msg)
                sys.exit(msg)
        except AttributeError as ex:
            msg = 'critical setup camera id {} - {}. Aborting!'.format(self._camera_id, ex)
            _log.critical(msg)
            sys.exit(msg)

    def calibrate(self):
        """Get image, resize, gray, blur"""
        # get new image
        (grabbed, frame) = self._cam.read()
        # test reading camera
        if not grabbed:
            _log.critical('error reading frame from camera')
            sys.exit('abnormal program termination!')
        # resize camera frame
        self.frame = imutils.resize(self.frame, self._width, self._height)
        self.frame = frame[1:self._height, 1:self._width]
        # gray conversion
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # blur conversion
        self._gray_frame = cv2.GaussianBlur(gray_frame, (self._gaussian_blur_value, self._gaussian_blur_value), 0)
        if self.first_frame is None:
            self.first_frame = gray_frame

    @property
    def objects(self):
        """ Compute the absolute difference between the current frame and first frame and find contours """
        self.calibrate()
        frame_delta = cv2.absdiff(self.first_frame, self._gray_frame)
        thresh = cv2.threshold(frame_delta, self._threshold_value, 255, cv2.THRESH_BINARY)[1]
        # dilate the thresholds image to fill in holes, then find contours on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        im2, self._contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for obj in self._contours:
            if cv2.contourArea(obj) > self._min_detect_area:
                yield obj

    def close(self):
        self._cam.release()
        _log.debug('closing camera')


def main():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    camera_data = {'camera_id': 0, 'camera_delay': 2, 'camera_width': 640, 'camera_height': 480,
                   'gaussian_blur_value': 21, 'min_detect_area': 3000, 'threshold_value': 60}
    cam = Camera(camera_data)
    cam.calibrate()
    sleep(1)
    for a in cam.objects:
        print(a)
    

if __name__ == '__main__':
    main()
