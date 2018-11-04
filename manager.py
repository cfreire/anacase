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
black_color = (0, 0, 0)
red_color = (0, 0, 255)
green_color = (0, 255, 0)
blue_color = (255, 0, 0)
gray_color = (98, 98, 98)
beacon_color = (0, 255, 0)
light_color = (238, 255, 170)
low_color = (102, 128, 0)

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
            self._beam_position = list(int(val) for val in display_data['beam_position'].split(','))  # x1, y1, x2, y2
            self._beam_dead_zone = int(display_data['beam_dead_zone'])
            self._height = int(display_data['image_height'])
            self._width = int(display_data['image_width'])
            self._bag_select = float(display_data['bag_select'])
            self._image_template = display_data['image_template']
            self._image_bag = display_data['image_bag']
            self._bag_datetime = datetime.datetime.now()
            self._mode_name = ['RUN', 'VIEW']
            self._mode_active = 0
            self._frame = None
            self._freeze = None
            self._alarm = False
            self._stats_active = False
            self._scanner = 0
            self._ack = False
            self.mark = False
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
                    cv2.FONT_HERSHEY_PLAIN, 1, light_color, 1)
        cv2.putText(self._frame, '{:04d}'.format(self._stats.counter), (50, 446),
                    cv2.FONT_HERSHEY_DUPLEX, 1.2, black_color, 3)
        cv2.putText(self._frame, '{:04d}'.format(self._stats.counter), (50, 446),
                    cv2.FONT_HERSHEY_DUPLEX, 1.2, white_color, 1)
        cv2.putText(self._frame, 'bag selected', (170, 412),
                    cv2.FONT_HERSHEY_PLAIN, 1, light_color, 1)
        cv2.putText(self._frame, '{:04d}'.format(self._stats.sampled), (170, 446),
                    cv2.FONT_HERSHEY_DUPLEX, 1.2, black_color, 3)
        cv2.putText(self._frame, '{:04d}'.format(self._stats.sampled), (170, 446),
                    cv2.FONT_HERSHEY_DUPLEX, 1.2, white_color, 1)
        cv2.putText(self._frame, 'selected %', (290, 412),
                    cv2.FONT_HERSHEY_PLAIN, 1, light_color, 1)
        cv2.putText(self._frame, '{:4.1f}'.format(self._stats.percentage), (290, 446),
                    cv2.FONT_HERSHEY_DUPLEX, 1.2, black_color, 3)
        cv2.putText(self._frame, '{:4.1f}'.format(self._stats.percentage), (290, 446),
                    cv2.FONT_HERSHEY_DUPLEX, 1.2, white_color, 1)
        cv2.putText(self._frame, 'mode', (410, 412),
                    cv2.FONT_HERSHEY_PLAIN, 1,light_color, 1)
        cv2.putText(self._frame, self._mode_name[self._mode_active], (410, 446),
                    cv2.FONT_HERSHEY_DUPLEX, 1.2, black_color, 3)
        cv2.putText(self._frame, self._mode_name[self._mode_active], (410, 446),
                    cv2.FONT_HERSHEY_DUPLEX, 1.2, white_color, 1)
        cv2.putText(self._frame, 'time', (730, 412),
                    cv2.FONT_HERSHEY_PLAIN, 1, light_color, 1)
        cv2.putText(self._frame, datetime.datetime.now().strftime("%H:%M:%S"), (600, 446),
                    cv2.FONT_HERSHEY_DUPLEX, 1.2, black_color, 3)
        cv2.putText(self._frame, datetime.datetime.now().strftime("%H:%M:%S"), (600, 446),
                    cv2.FONT_HERSHEY_DUPLEX, 1.2, white_color, 1)
        cv2.putText(self._frame, 'v{}'.format(self._software_version), (700, 472),
                    cv2.FONT_HERSHEY_PLAIN, 1.2, low_color, 1)

    def compute_img(self):
        """See if objects pass beam"""
        self._frame = cv2.imread(self._image_template, cv2.IMREAD_ANYCOLOR)             # read background image
        if self._mode_active:                                                           # VIEW MODE
            self._frame = cv2.add(self._frame, self.cam.frame)                          # add camera live view
            if (self._start_time + self._time_min_delta) < datetime.datetime.now():     # test if timeout
                cv2.line(self._frame, (self._beam_position[0], self._beam_position[1]),  # draw green line threshold
                         (self._beam_position[2], self._beam_position[3]), green_color, 2)
            else:
                cv2.line(self._frame, (self._beam_position[0], self._beam_position[1]),  # draw red line threshold
                         (self._beam_position[2], self._beam_position[3]), red_color, 2)
        self.draw_data()                                                                # draw info text
        for id_, obj in enumerate(self.cam.objects, 1):
            M = cv2.moments(obj)
            centro = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))               # calc contour center (x,y)
            if self._mode_active:                                                       # VIEW MODE
                cv2.line(self._frame, centro, centro, green_color, 3)                   # draw contours centroid
                (x, y, w, h) = cv2.boundingRect(obj)
                cv2.rectangle(self._frame, (x, y), (x + w, y + h), green_color, 1)      # draw contours in objects
                cv2.putText(self._frame, str(id_), centro, cv2.FONT_HERSHEY_PLAIN, 1, green_color, 1)
            # test if time as passed from last detection
            if (self._start_time + self._time_min_delta) < datetime.datetime.now():
                # test if center of object is before beam position
                if self._beam_position[1] - self._beam_dead_zone <= centro[1] <= self._beam_position[3]\
                        and self._beam_position[0] <= centro[0] <= self._beam_position[2]:
                    self.mark = True
                # test if center of object is before beam position
                if self.mark and self._beam_position[1] <= centro[1] <= self._beam_position[3] + self._beam_dead_zone\
                        and self._beam_position[0] <= centro[0] <= self._beam_position[2]:
                    self._stats.inc_counter()
                    log.debug("new bag detected. id={:03d} ".format(self._stats.counter))
                    self._start_time = datetime.datetime.now()
                    self._led_manager.activate_green()
                    self._scanner = 1

            if (self._start_time + self._time_min_delta) > datetime.datetime.now():
                self.mark = False
                if self._scanner > 0:
                    try:
                        bag = cv2.imread(self._image_bag)
                        self._frame = cv2.add(self._frame, bag)
                    except cv2.error:
                        log.error('error loading image "{}"'.format(self._image_bag))
                    self._frame = cv2.line(self._frame, (270, 200 + self._scanner), (440, 200 + self._scanner),
                                           green_color, 2)
                    self._scanner += 10
                if self._scanner > 100:
                    self._scanner = 0

    def show_stats(self):
        if self._stats_active:
            t = self._stats.counter_by_time
            cv2.putText(self._frame, 'bag counter on last 5/15/60 min.', (50, 90),
                        cv2.FONT_HERSHEY_PLAIN, 1.2, low_color, 1)
            cv2.putText(self._frame, '{:04d}/{:04d}/{:04d}'.format(t['min5'], t['min15'], t['min60']), (50, 130),
                        cv2.FONT_HERSHEY_DUPLEX, 1.4, white_color, 1)
            t = self._stats.selected_by_time
            cv2.putText(self._frame, 'bag selected on last 5/15/60 min.', (50, 170),
                        cv2.FONT_HERSHEY_PLAIN, 1.2, low_color, 1)
            cv2.putText(self._frame, '{:04d}/{:04d}/{:04d}'.format(t['min5'], t['min15'], t['min60']), (50, 210),
                        cv2.FONT_HERSHEY_DUPLEX, 1.4, white_color, 1)
            cv2.putText(self._frame, 'first bag seen on', (50, 250),
                        cv2.FONT_HERSHEY_PLAIN, 1.2, low_color, 1)
            cv2.putText(self._frame, self._stats.first_counter.strftime("%d/%m %H:%M:%S"), (50, 290),
                        cv2.FONT_HERSHEY_DUPLEX, 1.4, white_color, 1)
            cv2.putText(self._frame, '60min rate', (480, 90),
                        cv2.FONT_HERSHEY_PLAIN, 1.2, low_color, 1)
            cv2.putText(self._frame, '{:4.1f}%'.format(self._stats.percentage_by_time), (470, 130),
                        cv2.FONT_HERSHEY_DUPLEX, 1.4, white_color, 3)
            cv2.putText(self._frame, 'OPER ACK', (480, 170),
                        cv2.FONT_HERSHEY_PLAIN, 1.2, low_color, 1)
            cv2.putText(self._frame, ' {:04d}'.format(self._stats.ack), (470, 210),
                        cv2.FONT_HERSHEY_DUPLEX, 1.4, white_color, 3)
            cv2.putText(self._frame, 'v{}'.format(self._software_version), (700, 472),
                        cv2.FONT_HERSHEY_PLAIN, 1.2, low_color, 1)

    def case_for_review(self):
        """Detect if object is for review"""
        if self._stats.is_selected() and not self._alarm:
            self._bag_datetime = datetime.datetime.now()
            self._alarm = True
            self._freeze = self.cam.frame
            self._led_manager.activate_red()
            self._buzzer.activate_buzzer()
        if self._alarm:
            self._frame = cv2.add(self._frame, self._freeze)
            self._frame = cv2.rectangle(self._frame, (385, 36), (515, 62), red_color, -1)
            self._frame = cv2.putText(self._frame, 'SNAPSHOT', (400, 54), cv2.FONT_HERSHEY_DUPLEX, 0.6, white_color)
        timeout = self._bag_datetime + datetime.timedelta(seconds=self._bag_select)  # clear image after timeout
        if self._alarm and (timeout < datetime.datetime.now()):
            log.debug('reset review alarm at {}'.format(datetime.datetime.now()))
            self._alarm = None
        if self._ack and self._alarm:
            self._alarm = None
            self._ack = False
            self._stats.inc_ack()

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
        menu = {'mode': (23, 80), 'cal': (64, 150), 'reset': (184, 240),
                'stats': (253, 285), 'quit': (300, 360)}
        if event == cv2.EVENT_LBUTTONDOWN:
            log.debug('mouse clicked at {}x{}'.format(x, y))
            if x >= 600:
                if menu['mode'][0] < y < menu['mode'][1]:
                    self._mode_active += 1
                    if self._mode_active >= len(self._mode_name):
                        self._mode_active = 0
                    log.debug('mode selected "{}"'.format(self._mode_name[self._mode_active]))
                elif menu['cal'][0] < y < menu['cal'][1]:
                    self.cam.first_frame = None
                    log.debug('click on calibration')
                elif menu['reset'][0] < y < menu['reset'][1]:
                    log.debug('click on reset')
                    self._stats.reset()
                elif menu['stats'][0] < y < menu['stats'][1]:
                    log.debug('click on stats')
                    if self._stats_active:
                        self._stats_active = False
                    else:
                        self._stats_active = True
                elif menu['quit'][0] < y < menu['quit'][1]:
                    log.debug('click on quit')
                    self.close()
            if x <= 600:
                self._ack = True

    def run(self):
        self.compute_img()
        self.case_for_review()
        self.show_stats()
        self._led_manager.clear_leds()
        self._buzzer.stop_buzzer()
        self.display.update(self._frame)
        return App._wait_keypress()

    def close(self):
        self.cam.close()
        log.info('ending APP')
        sys.exit(0)
