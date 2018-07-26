import numpy as np
import datetime
import cv2
import logging
import sys

import display
import camera
import buzzer
import leds
import stats

# colors
white_color = (255, 255, 255)
red_color = (0, 0, 255)
green_color = (0, 255, 0)
blue_color = (255, 0, 0)
gray_color = (98, 98, 98)
beacon_color = (0, 255, 0)

log = logging.getLogger(__name__)


class App:
    """ Manage raspi APP """

    def __init__(self, camera_data, display_data, led_data, buzzer_data, random_data, version):
        log.info('starting APP version "{}"'.format(version))
        try:
            self.display = display.Display()
            self.cam = camera.Camera(camera_data)
            self._led_manager = leds.Leds(led_data)
            self._buzzer = buzzer.Buzzer(buzzer_data)
            self._case_review = stats.Stats(random_data).random_samples
            self._software_version = version
            self._start_time = datetime.datetime.now()
            self._time_min_delta = datetime.timedelta(seconds=float(display_data['time_min_delta']))
            self._beam_position = int(display_data['beam_position'])
            self._beam_dead_zone = int(display_data['beam_dead_zone'])
            self._height = int(display_data['image_height'])
            self._width = int(display_data['image_width'])
            self._bag_select = float(display_data['bag_select'])
            self._bag_datetime = datetime.datetime.now()
            self._operating = None
            self._frame = None
            self._alarm = False
            self._counter = 0
            self._freeze_frame = None
        except ValueError as ex:
            msg = 'error reading camera_data {}. Aborting!'.format(ex)
            log.error(msg)
            sys.exit(msg)

    def display_eng_mode(self):
        """ MODO ENG """
        self._frame = self.cam.frame
        self.display.window = 'ENGINEERING WINDOW'
        self.display.add_window_properties(cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback(self.display.window, self._mouse_clicks)
        cv2.line(self._frame, (self._beam_position, 50), (self._beam_position, self._height - 35), green_color, 2)
        cv2.rectangle(self._frame, (0, 0), (self._width, 30), gray_color, thickness=-1)  # upper gray
        cv2.putText(self._frame, "Counter: {:03d}".format(self._counter),
                    (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, white_color, 1)  # counter
        cv2.putText(self._frame, datetime.datetime.now().strftime("%H:%M:%S"),
                    (self._width - 100, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, white_color, 1)  # date at right
        cv2.rectangle(self._frame, (0, self._height), (self._width, self._height - 15),
                      gray_color, thickness=-1)

    def display_operating_mode(self):
        """  MODO OPERATION """
        if self._counter == 0:
            percent = 0
        else:
            percent = 51 - len(self._case_review)
        msg = "counter: {:03d} | selected: {:03d} | percentage: {:4.1f}%".format(self._counter, percent,
                            (51 - len(self._case_review)) / (self._counter+1) * 100)  # FIXME parameters
        if self._alarm:
            cv2.putText(self._freeze_frame, msg, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, white_color, 1)
            cv2.rectangle(self._freeze_frame, (0, 35), (self._width, self._height - 30), red_color, 20)
            self._frame = self._freeze_frame
        else:
            self._frame = np.zeros((self._height, self._width, 3), np.uint8)
            cv2.putText(self._frame, msg, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, white_color, 1)
            cv2.putText(self._frame, "{:03d}".format(self._counter), (self._height // 2, self._width // 2 - 100),
                        cv2.FONT_HERSHEY_DUPLEX, 5, white_color, 1)
        cv2.putText(self._frame, datetime.datetime.now().strftime("%H:%M:%S"),
                    (self._width - 100, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, white_color, 1)
        # clear image after timeout
        timeout = self._bag_datetime + datetime.timedelta(seconds=self._bag_select)
        if self._alarm and (timeout < datetime.datetime.now()):
            log.debug('reset review alarm at {}'.format(datetime.datetime.now()))
            self._alarm = None

    def lower_menu(self):
        cv2.putText(self._frame, 'QUIT', (10, self._height - 2), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, white_color, 1)
        cv2.putText(self._frame, 'CAL', (10 + 80, self._height - 2), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, white_color, 1)
        cv2.putText(self._frame, 'RESET', (10 + 80 * 2, self._height - 2), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, white_color, 1)
        cv2.putText(self._frame, 'OPER', (10 + 80 * 3, self._height - 2), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, white_color, 1)
        cv2.putText(self._frame, 'ENG', (10 + 80 * 4, self._height - 2), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, white_color, 1)
        cv2.putText(self._frame, self._software_version, (10 + 80 * 9, self._height - 2), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, white_color, 1)
        for i in range(10):
            cv2.line(self._frame, (i * 80, self._height), (i * 80, self._height - 15), white_color, 1)

    def case_for_review(self):
        """ Detect if case is for review"""
        if self._counter in self._case_review and not self._alarm:
            self._alarm = True
            self._case_review.remove(self._counter)  # remove case from list
            log.info('case {} select for review at {}'.format(self._counter, datetime.datetime.now()))
            self._bag_datetime = datetime.datetime.now()
            self._freeze_frame = self._frame
            self._led_manager.activate_red()
            self._buzzer.activate_buzzer()

    def compute_img(self):
        """See if objects pass beam"""
        img_objects = self.cam.objects
        for obj in img_objects:
            # calcular centro do contour
            M = cv2.moments(obj)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            # draw windows objects in eng mode
            if not self._operating:
                cv2.line(self._frame, (cx, cy), (cx, cy), green_color, 3)
                (x, y, w, h) = cv2.boundingRect(obj)
                cv2.rectangle(self._frame, (x, y), (x + w, y + h), green_color, 1)

            # test if center of object near beam position
            if self._beam_position - self._beam_dead_zone <= cx <= self._beam_position + self._beam_dead_zone and \
                    (self._start_time + self._time_min_delta) < datetime.datetime.now():
                self._counter += 1
                log.debug("counter {} ".format(self._counter))
                self._start_time = datetime.datetime.now()
            # reset _counter
            if self._counter >= 1000:  # FIXME parameter loop
                log.debug('counter recycled at 1000')
                self._counter = 0

    def run(self):
        self.compute_img()
        if self._operating:
            self.case_for_review()
            self.display_operating_mode()
        else:
            self.display_eng_mode()
        self.lower_menu()
        self.display.show(self._frame)
        # self._led_manager.clear_leds()
        # self._buzzer.stop_buzzer()
        return App._wait_keypress()

    @staticmethod
    def _wait_keypress():
        """ Test if key is pressed """
        key = cv2.waitKey(1) & 0xFF
        # if the `q` key is pressed
        if key == ord("q"):
            log.debug('q pressed. Quiting')
            return False
        else:
            return True

    def _mouse_clicks(self, event, x, y, flags, params):
        """ detect mouse / touch events """
        if event == cv2.EVENT_LBUTTONDOWN:
            if y >= self._height - 15:
                if 0 < x < 80:  # quit
                    sys.exit()
                elif 80 <= x < 80*2:  # cal
                    log.info('doing calibration')
                    self.cam.first_frame = None
                elif 80*2 <= x < 80*3:  # reset
                    log.info('reset counter at {}'.format(self._counter))
                    self._counter = 0
                elif 80*3 <= x < 80*4:  # start _operating
                    log.info('start operating mode')
                    self._operating = True
                elif 80*4 <= x < 80*5:  # start _operating
                    log.info('start eng mode')
                    self._operating = False

    def close(self):
        self.cam.close()
        log.info('    ... end ...')
