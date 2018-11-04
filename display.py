import cv2
import logging

log = logging.getLogger(__name__)


class Display:
    """Manages displays"""

    log = logging.getLogger(__name__)

    def __init__(self):
        self.keyboard_events = None
        self.mouse_clicks = None
        self._active_window = None
        self._display = []
        self.log.info('success creating display manager')

    @property
    def window(self):
        """get active window"""
        if self._active_window:
            return self._active_window

    @window.setter
    def window(self, window_title):
        """activate window or create new one if not exists"""
        if window_title in self._display:
            self._active_window = window_title
            self.log.debug('activating window "{}"'.format(window_title))
        else:
            self._display.append(window_title)
            cv2.namedWindow(window_title, cv2.WND_PROP_AUTOSIZE)
            self._active_window = window_title
            self.log.debug('creating new window "{}"'.format(window_title))

    @window.deleter
    def window(self):
        """delete active window"""
        self.log.debug('deleting window "{}"'.format(self._active_window))
        self._display.remove(self._active_window)
        cv2.destroyWindow(self._active_window)
        self._active_window = None

    def update(self, frame=None):
        """show window"""
        if self._active_window:
            cv2.imshow(self._active_window, frame)

    def add_window_properties(self, *parameters):
        if self._active_window:
            cv2.setWindowProperty(self._active_window, *parameters)
        else:
            log.warning('no active window')
            raise ValueError('no active window')

    def __del__(self):
        cv2.destroyAllWindows()


def main():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    m = Display()
    m.window = 'debug'
    m.add_window_properties(cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    m.update(0)
    cv2.waitKey(0)


if __name__ == '__main__':
    main()
