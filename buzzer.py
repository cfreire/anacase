import logging
import datetime
from platform import machine
from time import sleep

log = logging.getLogger(__name__)

RASPI = ["armv7l"]

if machine() in RASPI:
    import RPi.GPIO as Io


class Buzzer:

    def __init__(self, buzzer_param):
        self._alarm = None
        self.timeout = float(buzzer_param['timeout'])
        self.buzzer_datetime = datetime.datetime.now()
        if machine() in RASPI:
            log.info('activate buzzer module on platform {}'.format(machine()))
            Io.setmode(Io.BCM)
            Io.setup(13, Io.OUT)
            self._buzzer = Io.PWM(13, 100)
        else:
            log.warning('no support for buzzer on platform {}'.format(machine()))

    def activate_buzzer(self):
        if not self._alarm:
            log.debug('buzzer activated')
            self._alarm = True
            if machine() in RASPI:
                self._buzzer.start(50)
            else:
                pass

    def stop_buzzer(self):
        timeout = self.buzzer_datetime + datetime.timedelta(seconds=self.timeout)
        if self._alarm and (timeout < datetime.datetime.now()):
            log.debug('buzzer stopped')
            self._alarm = False
        if machine() in RASPI:
            self._buzzer.stop()
        else:
            pass

    def __del__(self):
        if machine() in RASPI:
            Io.cleanup()


if __name__ == "__main__":
    # simple explore test
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    buzzer_data = {'timeout': '2.0'}
    b = Buzzer(buzzer_data)
    b.activate_buzzer()
    for n in range(1, 2000):
        sleep(0.001)
        b.stop_buzzer()

