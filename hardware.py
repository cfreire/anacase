__version__ = '1.0.0'

import cv2
import logging

log = logging.getLogger(__name__)


class Manager:
    """Manages project hardware, like display

     display, keyboard, mouse, buzzer, leds, etc...
    """

    log = logging.getLogger(__name__)

    def __init__(self,  keyboard=None, mouse=None, buzzer=None, leds=None):
        self._windows = []
        self._active_window = None
        self._keyboard = keyboard
        self._mouse_events = mouse
        self._buzzer = buzzer
        self._leds = leds
        self.log.info('success creating manager')

    # display ###############################################################

    @property
    def window(self):
        """get active window"""
        if self._active_window:
            return self._active_window

    @window.setter
    def window(self, window_title):
        """activate window or create new one if not exists"""
        if window_title in self._windows:
            self._active_window = window_title
            self.log.debug('activating window "{}"'.format(window_title))
        else:
            self._windows.append(window_title)
            cv2.namedWindow(window_title, cv2.WND_PROP_AUTOSIZE)
            self._active_window = window_title
            self.log.debug('creating new window "{}"'.format(window_title))

    @window.deleter
    def window(self):
        """delete active window"""
        self.log.debug('deleting window "{}"'.format(self._active_window))
        self._windows.remove(self._active_window)
        cv2.destroyWindow(self._active_window)
        self._active_window = None

    def show(self, frame=None):
        """show window"""
        if self._active_window:
            cv2.imshow(self._active_window, frame)
            return Manager.process_events()

    def add_window_properties(self, *parameters):
        if self._active_window:
            cv2.setWindowProperty(self._active_window, *parameters)
        else:
            log.warning('no active window')
            raise ValueError('no active window')

    @staticmethod
    def process_events():
        """ Test if key is pressed """
        key = cv2.waitKey(1) & 0xFF
        # if the `q` key is pressed
        if key == ord("q"):
            return False
        else:
            return True


def main():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    m = Manager()
    m.window = 'debug'
    m.add_window_properties(cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    while m.show(0):
        pass


if __name__ == '__main__':
    main()
