from time import sleep
import numpy as np
import imutils
import datetime
import cv2
import logging
import sys

import leds
import buzzer

_log = logging.getLogger(__name__)


class Camera:
    """ Camera setup and motion detect """
    _frame = None
    first_frame = None
    gray_frame = None
    _cam = None
    contours = None

    def __init__(self, camera_data, led_data, random_data, buzzer_data, version):
        # get vars
        try:
            self._software_version = version
            self._alarm = False
            self._counter = 0
            self._freeze_frame = None
            self._camera_id = int(camera_data['camera_id'])
            self._start_time = datetime.datetime.now()
            self._time_min_delta = datetime.timedelta(seconds=float(camera_data['time_min_delta']))
            self._beam_position = int(camera_data['beam_position'])
            self._beam_dead_zone = int(camera_data['beam_dead_zone'])
            self._width = int(camera_data['image_width'])
            self._height = int(camera_data['image_height'])
            self._min_detect_area = int(camera_data['min_detect_area'])
            self._window_name = camera_data['window_title']
            self._gaussian_blur_value = int(camera_data['gaussian_blur_value'])
            self._threshold_value = int(camera_data['threshold_value'])
            self._camera_delay = int(camera_data['camera_delay'])
            self._bag_select = float(camera_data['bag_select'])
            self._bag_datetime = datetime.datetime.now()
            self._case_review = random_data
            self._led_manager = leds.Leds(led_data)
            self._buzzer = buzzer.Buzzer(buzzer_data)
            _log.info('starting v4l on camera id "{}"'.format(self._camera_id))
        except ValueError as ex:
            msg = 'error reading camera_data {}. Aborting!'.format(ex)
            _log.error(msg)
            sys.exit(msg)

        try:
            self._cam = cv2.VideoCapture(self._camera_id)
            self._cam.set(3, 640)  # FIXME parameters
            self._cam.set(4, 480)  # FIXME parameters
            sleep(self._camera_delay)
            (grabbed, self._frame) = self._cam.read()
            if not grabbed:  # error in camera
                msg = 'error reading _frame on camera id "{}. Aborting!"'.format(self._camera_id)
                _log.critical(msg)
                sys.exit(msg)
        except AttributeError as ex:
            msg = 'critical setup camera id {} - {}. Aborting!'.format(self._camera_id, ex)
            _log.critical(msg)
            sys.exit(msg)

        # colors
        self._white_color = (255, 255, 255)
        self._red_color = (0, 0, 255)
        self._green_color = (0, 255, 0)
        self._blue_color = (255, 0, 0)
        self._gray_color = (98, 98, 98)
        self._beacon_color = (0, 255, 0)
        self._operating = True
        # set display size
        cv2.namedWindow(self._window_name, cv2.WND_PROP_AUTOSIZE)
        cv2.setWindowProperty(self._window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback(self._window_name, self._click)

    def get_new_frame(self):
        """Get image, resize, gray, blur"""
        # get new image
        (grabbed, self._frame) = self._cam.read()
        # test reading camera
        if not grabbed:
            _log.critical('error reading frame from camera')
            sys.exit('abnormal program termination!')
        # resize camera _frame
        self._frame = imutils.resize(self._frame, self._width, self._height)
        self._frame = self._frame[1:self._height, 1:self._width]
        # gray conversion
        self.gray_frame = cv2.cvtColor(self._frame, cv2.COLOR_BGR2GRAY)
        # blur conversion
        self.gray_frame = cv2.GaussianBlur(self.gray_frame, (self._gaussian_blur_value, self._gaussian_blur_value), 0)
        if self.first_frame is None:
            self.first_frame = self.gray_frame

    def compute_img(self):
        """ Compute the absolute difference between the current frame and first frame and find contours """
        self.get_new_frame()
        frame_delta = cv2.absdiff(self.first_frame, self.gray_frame)
        thresh = cv2.threshold(frame_delta, self._threshold_value, 255, cv2.THRESH_BINARY)[1]
        # dilate the thresholds image to fill in holes, then find contours on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        im2, self.contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in self.contours:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < self._min_detect_area:
                continue
            # calcular centro do contour
            M = cv2.moments(c)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            # draw windows objects in eng mode
            if not self._operating:
                cv2.line(self._frame, (cx, cy), (cx, cy), self._green_color, 3)
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(self._frame, (x, y), (x + w, y + h), self._green_color, 1)

            # test if center of object near beam position
            if self._beam_position - self._beam_dead_zone <= cx <= self._beam_position + self._beam_dead_zone and \
                    (self._start_time + self._time_min_delta) < datetime.datetime.now():
                self._counter += 1
                _log.debug("counter {} ".format(self._counter))
                self._led_manager.activate_green()
                self._start_time = datetime.datetime.now()
            # reset _counter
            if self._counter >= 1000: # FIXME parameter loop
                _log.debug('counter recycled at 1000')
                self._counter = 0

        # debug on X86
        # TODO debugger console
        # if platform.machine() != 'armv7l':
        #    cv2.imshow("Debug Delta", frame_delta)
        #    cv2.imshow("Debug Threshold", thresh)

    def display_eng_mode(self):
        """ MODO ENG """
        cv2.line(self._frame, (self._beam_position, 50),
                 (self._beam_position, self._height - 35), self._green_color, 2)  # beam
        cv2.rectangle(self._frame, (0, 0), (self._width, 30), self._gray_color, thickness=-1)  # upper gray
        cv2.putText(self._frame, "Counter: {:03d}".format(self._counter),
                    (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self._white_color, 1)  # counter
        cv2.putText(self._frame, datetime.datetime.now().strftime("%H:%M:%S"),
                    (self._width - 100, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self._white_color, 1)  # date at right
        cv2.rectangle(self._frame, (0, self._height), (self._width, self._height - 15),
                      self._gray_color, thickness=-1)

    def lower_menu(self):
        cv2.putText(self._frame, 'QUIT', (10, self._height - 2), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, self._white_color, 1)
        cv2.putText(self._frame, 'CAL', (10 + 80, self._height - 2), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, self._white_color, 1)
        cv2.putText(self._frame, 'RESET', (10 + 80*2, self._height - 2), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, self._white_color, 1)
        cv2.putText(self._frame, 'OPER', (10+80*3, self._height - 2), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, self._white_color, 1)
        cv2.putText(self._frame, 'ENG', (10+80*4, self._height - 2), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, self._white_color, 1)
        cv2.putText(self._frame,  self._software_version, (10 + 80 * 9, self._height - 2), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, self._white_color, 1)

        for i in range(10):
            cv2.line(self._frame, (i * 80, self._height), (i * 80, self._height - 15), self._white_color, 1)

    def display_operating_mode(self):
        """  MODO OPERATION """
        msg = "counter: {:03d} | selected: {:03d} | percentage: {:4.1f}%".format(self._counter, 101 - len(self._case_review),
                                                  (101 - len(self._case_review)) / (self._counter+1) * 100)  # FIXME parameters
        if self._alarm:
            cv2.putText(self._freeze_frame, msg, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self._white_color, 1)
            cv2.rectangle(self._freeze_frame, (0, 35), (self._width, self._height - 30), self._red_color, 20)
            self._frame = self._freeze_frame
        else:
            self._frame = np.zeros((self._height, self._width, 3), np.uint8)
            cv2.putText(self._frame, msg, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self._white_color, 1)
            cv2.putText(self._frame, "{:03d}".format(self._counter), (self._height // 2, self._width // 2 - 100),
                        cv2.FONT_HERSHEY_DUPLEX, 5, self._white_color, 1)
        cv2.putText(self._frame, datetime.datetime.now().strftime("%H:%M:%S"),
                    (self._width - 100, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self._white_color, 1)
        # clear image after timeout
        timeout = self._bag_datetime + datetime.timedelta(seconds=self._bag_select)
        if self._alarm and (timeout < datetime.datetime.now()):
            _log.debug('reset review alarm at {}'.format(datetime.datetime.now()))
            self._alarm = None

    def case_for_review(self):
        """ Detect if case is for review"""
        if self._counter in self._case_review and not self._alarm:
            self._alarm = True
            self._case_review.remove(self._counter)  # remove case from list
            _log.info('case {} select for review at {}'.format(self._counter, datetime.datetime.now()))
            self._bag_datetime = datetime.datetime.now()
            self._freeze_frame = self._frame
            self._led_manager.activate_red()
            self._buzzer.activate_buzzer()

    def run(self):
        self.compute_img()
        if self._operating:
            self.case_for_review()
            self.display_operating_mode()
        else:
            self.display_eng_mode()
        self.lower_menu()
        cv2.imshow(self._window_name, self._frame)
        self._led_manager.clear_leds()
        self._buzzer.stop_buzzer()
        return Camera.wait_keypress()

    @staticmethod
    def wait_keypress():
        """ Test if key is pressed """
        key = cv2.waitKey(1) & 0xFF
        # if the `q` key is pressed
        if key == ord("q"):
            _log.debug('q pressed. Quiting')
            return False
        else:
            return True

    def _click(self, event, x, y, flags, params):
        """ detect mouse / touch events """
        if event == cv2.EVENT_LBUTTONDOWN:
            if y >= self._height - 15:
                if 0 < x < 80:  # quit
                    sys.exit()
                elif 80 <= x < 80*2:  # cal
                    _log.info('doing calibration')
                    self.first_frame = None
                elif 80*2 <= x < 80*3:  # reset
                    _log.info('reset counter at {}'.format(self._counter))
                    self._counter = 0
                elif 80*3 <= x < 80*4:  # start _operating
                    _log.info('start operating mode')
                    self._operating = True
                elif 80*4 <= x < 80*5:  # start _operating
                    _log.info('start eng mode')
                    self._operating = False

    def close(self):
        self._cam.release()
        cv2.destroyAllWindows()
        _log.info('    ... end ...')
