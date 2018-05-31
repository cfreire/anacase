__version__ = '1.0.3'

import platform
import datetime
import logging
import time

log = logging.getLogger(__name__)

MACHINE = platform.machine()
RASPI = ["armv7l"]

if MACHINE in RASPI:
    from gpiozero import LED


class Leds:
    """ LED's manager, control _led_red and _led_green led """

    def __init__(self, led_param):
        if MACHINE in RASPI:
            self._led_green = LED(int(led_param['green_gpio']))
            self._led_red = LED(int(led_param['red_gpio']))
            log.info('activate led module on platform {}'.format(MACHINE))
        else:
            log.warning('no support for leds on platform {}'.format(MACHINE))

        self._green_timeout = float(led_param['green_timeout'])
        self._red_timeout = float(led_param['red_timeout'])
        self._green_datetime = datetime.datetime.now()
        self._red_datetime = datetime.datetime.now()
        self._red_active = False
        self._green_active = False

    def activate_red(self):
        if not self._red_active:
            log.debug('red led on')
            self._red_active = True
            self._red_datetime = datetime.datetime.now()
            if MACHINE in RASPI:
                try:
                    self._led_red.on()
                except:
                    log.warning('red led gpio fail on [{}]'.format(self._led_red))
        return self._red_active

    def activate_green(self):
        if not self._green_active and not self._red_active:
            log.debug('green led on')
            self._green_active = True
            self._green_datetime = datetime.datetime.now()
            if MACHINE in RASPI:
                try:
                    self._led_green.on()
                except:
                    log.warning('green led gpio fail on [{}]'.format(self._led_green))
        return self._green_active

    def clear_leds(self):
        timeout_green = self._green_datetime + datetime.timedelta(seconds=self._green_timeout)
        if self._green_active and (timeout_green < datetime.datetime.now()):
            log.debug('green led off')
            self._green_active = False
            if MACHINE in RASPI:
                try:
                    self._led_green.off()
                except:
                    log.warning('green led off gpio fail on [{}]'.format(self._led_green))
        timeout_red = self._red_datetime + datetime.timedelta(seconds=self._red_timeout)
        if self._red_active and (timeout_red < datetime.datetime.now()):
            log.debug('red led off')
            self._red_active = False
            if MACHINE in RASPI:
                try:
                    self._led_red.off()
                except:
                    log.warning('red led off gpio fail on [{}]'.format(self._led_red))
        return [self._red_active, self._green_active]


if __name__ == "__main__":
    # simple explore test
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    led_data = {'red_gpio': '20', 'red_timeout': '2', 'green_gpio': '21', 'green_timeout': '3'}
    led = Leds(led_data)
    led.activate_green()
    time.sleep(1)
    print('1 second')
    led.clear_leds()
    time.sleep(2)
    print('2 seconds')
    led.clear_leds()
    led.activate_red()
    time.sleep(1)
    print('1 second')
    led.clear_leds()
    time.sleep(2)
    print('2 seconds')
    led.clear_leds()
