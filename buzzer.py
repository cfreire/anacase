__version__ = "1.0.7"

import platform
import logging
from time import sleep

log = logging.getLogger(__name__)

MACHINE = platform.machine()
RASPI = ["armv7l"]

if MACHINE in RASPI:
    import RPi.GPIO as Io


class Buzzer:

    def __init__(self):
        self._alarm = False
        if MACHINE in RASPI:
            if not self._alarm:
                log.debug('setup buzzer')
                Io.setmode(Io.BCM)
                Io.setup(13, Io.OUT)
                self._buzzer = Io.PWM(13, 100)

    def activate_buzzer(self):
        if not self._alarm:
            log.debug('buzzer activated')
            if MACHINE in RASPI:
                self._buzzer.start(50)
            else:
                pass

    def stop_buzzer(self):
        if self._alarm:
            log.debug('buzzer stopped')
        if MACHINE in RASPI:
            self._buzzer.stop()
        else:
            pass


if __name__ == "__main__":
    # simple explore test
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    b = Buzzer()
    b.activate_buzzer()
    sleep(1)
    b.stop_buzzer()
