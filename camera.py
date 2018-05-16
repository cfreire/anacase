from time import sleep
import numpy as np
import imutils
import datetime
import cv2
import logging
import sys
import platform

import leds

_log = logging.getLogger(__name__)


class Camera:
    """ Camera setup and motion detect """
    _frame = None
    first_frame = None
    gray_frame = None
    _cam = None
    contours = None

    def __init__(self, camera_data, led_data, random_data):
        # get vars
        try:
            self._counter = 0
            self._alarm = False
            self.p = None
            self._camera_id = int(camera_data['camera_id'])
            self._start_time = datetime.datetime.now()
            self._time_min_delta = datetime.timedelta(seconds=float(camera_data['time_min_delta']))
            self._beam_position = int(camera_data['beam_position'])
            self._beam_dead_zone = int(camera_data['beam_dead_zone'])
            self._width = int(camera_data['image_width'])
            self._height = int(camera_data['image_height'])
            self._min_detect_area = int(camera_data['min_detect_area'])
            self._window_name = camera_data['window_title']
            self.gaussian_blur_value = int(camera_data['gaussian_blur_value'])
            self.threshold_value = int(camera_data['threshold_value'])
            self._camera_delay = int(camera_data['camera_delay'])
            self._case_review = random_data
            self._led_manager = leds.Leds(led_data)
            _log.info(f'starting v4l on camera id "{self._camera_id}"')
        except ValueError as ex:
            msg = f'error reading camera_data {ex}. Aborting!'
            _log.error(msg)
            sys.exit(msg)

        try:
            self._cam = cv2.VideoCapture(self._camera_id)
            sleep(self._camera_delay)
            (grabbed, self._frame) = self._cam.read()
            if not grabbed:  # error in camera
                msg = f'error reading _frame on camera id "{self._camera_id}. Aborting!"'
                _log.critical(msg)
                sys.exit(msg)
        except AttributeError as ex:
            msg = f'critical setup camera id {self._camera_id} - {ex}. Aborting!'
            _log.critical(msg)
            sys.exit(msg)

        # colors
        self._white_color = (255, 255, 255)
        self._red_color = (0, 0, 255)
        self._green_color = (0, 255, 0)
        self._blue_color = (255, 0, 0)
        self._gray_color = (98, 98, 98)
        self._beacon_color = (0, 255, 0)
        self._operating = False
        # set display size
        cv2.namedWindow(self._window_name, cv2.WND_PROP_AUTOSIZE)
        cv2.setWindowProperty(self._window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    def get_new_frame(self):
        """Get image, resize, gray, blur"""
        # get new image
        (grabbed, self._frame) = self._cam.read()
        # test reading camera
        if not grabbed:
            _log.log(logging.CRITICAL, 'error reading _frame from camera')
            sys.exit('abnormal program termination!')
        # resize camera _frame
        self._frame = imutils.resize(self._frame, self._width, self._height)
        # gray conversion
        self.gray_frame = cv2.cvtColor(self._frame, cv2.COLOR_BGR2GRAY)
        # blur conversion
        self.gray_frame = cv2.GaussianBlur(self.gray_frame, (self.gaussian_blur_value, self.gaussian_blur_value), 0)
        if self.first_frame is None:
            self.first_frame = self.gray_frame

    def compute_img(self):
        """ Compute the absolute difference between the current _frame and first _frame and find contours """
        self.get_new_frame()
        frame_delta = cv2.absdiff(self.first_frame, self.gray_frame)
        thresh = cv2.threshold(frame_delta, self.threshold_value, 255, cv2.THRESH_BINARY)[1]
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
            # draw windows objects
            if not self._operating:
                cv2.line(self._frame, (cx, cy), (cx, cy), self._green_color, 3)
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(self._frame, (x, y), (x + w, y + h), self._green_color, 1)
            # test if center of object near beam position
            if self._beam_position - self._beam_dead_zone <= cx <= self._beam_position + self._beam_dead_zone and \
                    (self._start_time + self._time_min_delta) < datetime.datetime.now():
                self._counter += 1
                _log.debug(f"bag _counter ={self._counter} ")
                # _led_green led on raspberry
                self._led_manager.activate_green()
                self._start_time = datetime.datetime.now()
            # reset _counter
            if self._counter == 1000:
                self._counter = 0


        # =================
        # display
        # =================
        if not self._operating:
            """ MODO ENG """
            # beam
            cv2.line(self._frame, (self._beam_position, 50), (self._beam_position, self._height - 35),
                     self._green_color, 2)
            # upper gray
            cv2.rectangle(self._frame, (0, 0), (self._width, 30), self._gray_color, thickness=-1)
            # _counter
            cv2.putText(self._frame, "Counter: {:03d}".format(self._counter), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        self._white_color, 1)
            # date at right
            cv2.putText(self._frame, datetime.datetime.now().strftime("%B %Y %H:%M:%S"),
                        (self._width - 200, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self._white_color, 1)
            # lower menu
            cv2.rectangle(self._frame, (0, self._height), (self._width, self._height - 15), self._gray_color,
                          thickness=-1)
            cv2.putText(self._frame, 'QUIT', (10, self._height - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self._white_color,
                        1)
            cv2.putText(self._frame, 'CAL', (10 + 48, self._height - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        self._white_color,
                        1)
            cv2.putText(self._frame, 'RST', (10 + 96, self._height - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        self._white_color,
                        1)
            cv2.putText(self._frame, 'START', (144, self._height - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self._white_color,
                        1)
            for i in range(10):
                cv2.line(self._frame, (i * 48, self._height), (i * 48, self._height - 15), self._white_color, 1)

            # detect mouse events
            cv2.setMouseCallback(self._window_name, self._click)
            cv2.imshow(self._window_name, self._frame)

        else:
            """  MODO OPERATION """
            blank_image = np.zeros((self._height, self._width, 3), np.uint8)
            cv2.namedWindow(self._window_name, cv2.WND_PROP_AUTOSIZE)
            cv2.setWindowProperty(self._window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

            # seleccionado para revisão
            if self._counter in self._case_review:
                if not self._alarm:
                    blank_image = self._frame
                    cv2.rectangle(blank_image, (0, 30), (self._width, self._height - 15), self._red_color, 20)
                    self._alarm = True
                # led
                self._led_manager.activate_red()
                if platform.machine() == 'armv7':
                    # buzzer
                    if not self._alarm:
                        IO.setmode(IO.BCM)  # we are programming the GPIO by BCM pin numbers. (PIN35 as ‘GPIO19’)
                        IO.setup(13, IO.OUT)  # initialize GPIO19 as an output.
                        self.p = IO.PWM(13, 100)  # GPIO13 as PWM output, with 100Hz frequency
                        self.p.start(50)  # generate PWM signal with 50% duty cycle
            else:
                cv2.putText(blank_image, "{:03d}".format(self._counter), (self._height // 2, self._width // 2 - 100),
                            cv2.FONT_HERSHEY_DUPLEX, 5, self._white_color, 1)
            if self._counter not in self._case_review:
                self._alarm = False
                if platform.machine() == 'armv7l' and self.p is not None:
                    self.p.stop()
            # date at right
            cv2.putText(blank_image, datetime.datetime.now().strftime("%B %Y %H:%M:%S"),
                        (self._width - 200, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self._white_color, 1)

            cv2.imshow(self._window_name, blank_image)

        # debug on X86
        # TODO debugger console
        # if platform.machine() != 'armv7l':
        #    cv2.imshow("Debug Delta", frame_delta)
        #    cv2.imshow("Debug Threshold", thresh)

    @staticmethod
    def wait_keypress():
        """ Test if key is pressed """
        key = cv2.waitKey(1) & 0xFF
        # if the `q` key is pressed
        if key == ord("q"):
            return True

    def _click(self, event, x, y, flags, params):
        """ detect mouse / touch events """
        if event == cv2.EVENT_LBUTTONDOWN:
            if y >= self._height - 15:
                if 0 < x < 48:  # quit
                    sys.exit()
                elif 49 <= x <= 96:  # cal
                    _log.log(logging.INFO, 'doing calibration')
                    self.first_frame = None
                elif 97 <= x <= 144:  # reset
                    _log.log(logging.INFO, 'reset _counter at {}'.format(self._counter))
                    self._counter = 0
                elif 145 <= x <= 192:  # start _operating
                    _log.log(logging.INFO, 'start _operating')
                    self._operating = True

    def close(self):
        self._cam.release()
        cv2.destroyAllWindows()
        _log.info('    ... end ...')
