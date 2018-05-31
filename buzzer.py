__version__ = "1.0.0"

import platform
import logging
from time import sleep

log = logging.getLogger(__name__)

MACHINE = platform.machine()
RASPI = ["armv7l"]

if MACHINE in RASPI:
    from gpiozero import GPIODevice as Io


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
            if MACHINE in RASPI:
                log.debug('buzzer activated')
                self._buzzer.start(50)
            else:
                print('\a')

    def stop_buzzer(self):
        if MACHINE in RASPI and self._buzzer is not None:
            log.debug('buzzer stopped')
            self._buzzer.stop()


if __name__ == "__main__":
    # simple explore test
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    b = Buzzer()
    b.activate_buzzer()
    sleep(1)
    b.stop_buzzer()
