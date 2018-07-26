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
            self._stats = stats.Stats(random_data)
            self._software_version = version
            self._start_time = datetime.datetime.now()
            self._time_min_delta = datetime.timedelta(seconds=float(display_data['time_min_delta']))
            self._beam_position = int(display_data['beam_position'])
            self._beam_dead_zone = int(display_data['beam_dead_zone'])
            self._height = int(display_data['image_height'])
            self._width = int(display_data['image_width'])
            self._bag_select = float(display_data['bag_select'])
            self._image_template = display_data['image_template']
            self._bag_datetime = datetime.datetime.now()
            self._mode_name = ['RUN', 'VIEW']
            self._mode_active = 0
            self._frame = None
            self._alarm = False
        except ValueError as ex:
            msg = 'error reading camera_data {}. Aborting!'.format(ex)
            log.error(msg)
            sys.exit(msg)

        # start display
        self.display.window = 'ANACASE {}'.format(self._software_version)
        self.display.add_window_properties(cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback(self.display.window, self._mouse_clicks)

    def draw_data(self):
        """draw data on display"""
        cv2.putText(self._frame, 'bag counter', (50, 412),
                    cv2.FONT_HERSHEY_PLAIN, 1, white_color, 1)
        cv2.putText(self._frame, '{:03d}'.format(self._stats.counter), (50, 446),
                    cv2.FONT_HERSHEY_DUPLEX, 1.2, white_color, 1)
        cv2.putText(self._frame, 'bag selected', (170, 412),
                    cv2.FONT_HERSHEY_PLAIN, 1, white_color, 1)
        cv2.putText(self._frame, '{:03d}'.format(self._stats.sampled), (170, 446),
                    cv2.FONT_HERSHEY_DUPLEX, 1.2, white_color, 1)
        cv2.putText(self._frame, 'selected %', (290, 412),
                    cv2.FONT_HERSHEY_PLAIN, 1, white_color, 1)
        cv2.putText(self._frame, '{:4.1f}'.format(self._stats.percentage), (290, 446),
                    cv2.FONT_HERSHEY_DUPLEX, 1.2, white_color, 1)
        cv2.putText(self._frame, 'mode', (410, 412),
                    cv2.FONT_HERSHEY_PLAIN, 1, white_color, 1)
        cv2.putText(self._frame, self._mode_name[self._mode_active], (410, 446),
                    cv2.FONT_HERSHEY_DUPLEX, 1.2, white_color, 1)
        cv2.putText(self._frame, 'time', (600, 412),
                    cv2.FONT_HERSHEY_PLAIN, 1, white_color, 1)
        cv2.putText(self._frame, datetime.datetime.now().strftime("%H:%M:%S"), (600, 446),
                    cv2.FONT_HERSHEY_DUPLEX, 1.2, white_color, 1)

    def compute_img(self):
        """See if objects pass beam"""
        self._frame = cv2.imread(self._image_template, cv2.IMREAD_ANYCOLOR)  # read background image
        if self._mode_active == 1:
            self._frame = cv2.add(self._frame, self.cam.frame)
            cv2.line(self._frame, (self._beam_position, 50),
                     (self._beam_position, self._height - 100), green_color, 2)
        self.draw_data()  # draw info
        for obj in self.cam.objects:
            # calcular centro do contour
            M = cv2.moments(obj)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            # draw objects in ENG mode
            if self._mode_active != 0:
                cv2.line(self._frame, (cx, cy), (cx, cy), green_color, 3)
                (x, y, w, h) = cv2.boundingRect(obj)
                cv2.rectangle(self._frame, (x, y), (x + w, y + h), green_color, 1)

            # test if center of object near beam position
            if self._beam_position - self._beam_dead_zone <= cx <= self._beam_position + self._beam_dead_zone and \
                    (self._start_time + self._time_min_delta) < datetime.datetime.now():
                self._stats.inc_counter()
                log.debug("counter {} ".format(self._stats.counter))
                self._start_time = datetime.datetime.now()
        self.display.show(self._frame)

    def case_for_review(self):
        """Detect if object is for review"""
        if self._stats.is_selected() and not self._alarm:
            log.info('case {} select for review at {}'.format(self._stats.counter, datetime.datetime.now()))
            self._bag_datetime = datetime.datetime.now()
            self._alarm = True
            self._led_manager.activate_red()
            self._buzzer.activate_buzzer()
        if self._alarm:
            # TODO merge image
            # capture = self.cam.frame
            # cv2.copyMakeBorder(self._freeze_frame, capture)
            # self._freeze_frame = cv2.bitwise_and(self._frame, capture)
            cv2.rectangle(self._frame, (41, 81), (552, 336), red_color, 5)
        timeout = self._bag_datetime + datetime.timedelta(seconds=self._bag_select)  # clear image after timeout
        if self._alarm and (timeout < datetime.datetime.now()):
            log.debug('reset review alarm at {}'.format(datetime.datetime.now()))
            self._alarm = None

    @staticmethod
    def _wait_keypress():
        """ Test if key is pressed """
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):  # if the `q` key is pressed
            log.debug('q pressed. Quiting!')
            return False
        else:
            return True

    def _mouse_clicks(self, event, x, y, flags, params):
        """ detect mouse / touch events """
        menu = {'mode': (23, 80), 'cal': (64, 150), 'reset': (165, 187),
                'stats': (253, 290), 'quit': (300, 360), 'void': (375, 430)}
        if event == cv2.EVENT_LBUTTONDOWN:
            log.debug('mouse clicked at {}x{}'.format(x, y))
            if x >= 600:
                if menu['mode'][0] < y < menu['mode'][1]:
                    self._mode_active += 1
                    if self._mode_active >= len(self._mode_name):
                        self._mode_active = 0
                elif menu['cal'][0] < y < menu['cal'][1]:
                    self.cam.first_frame = None
                    log.debug('click in calibration')
                elif menu['reset'][0] < y < menu['reset'][1]:
                    self._counter = 0
                    log.debug('click in reset')
                elif menu['stats'][0] < y < menu['stats'][1]:
                    pass
                    log.debug('click in stats')
                elif menu['quit'][0] < y < menu['quit'][1]:
                    log.debug('click in quit')
                    sys.exit(1)
                elif menu['void'][0] < y < menu['void'][1]:
                    pass
                    log.debug('click in void')

    def run(self):
        self.compute_img()
        self.case_for_review()
        self._led_manager.clear_leds()
        self._buzzer.stop_buzzer()
        return App._wait_keypress()

    def close(self):
        self.cam.close()
        log.info('    ... end ...')
