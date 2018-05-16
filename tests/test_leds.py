import unittest
import leds
import time
import logging


class TestLedMethods(unittest.TestCase):

    def setUp(self):
        led_data = {'red_gpio': '20', 'red_timeout': '2', 'green_gpio': '21', 'green_timeout': '3'}
        self.led = leds.Leds(led_data)

    def test_activate_green_led(self):
        self.assertTrue(self.led.activate_green())
        time.sleep(1)
        self.assertEqual(self.led.clear_leds(), [False, True])  # red, green
        time.sleep(2)
        self.assertEqual(self.led.clear_leds(), [False, False])
        time.sleep(1)
        self.assertEqual(self.led.clear_leds(), [False, False])

    def test_activate_red_led(self):
        self.assertTrue(self.led.activate_red())
        time.sleep(1)
        self.assertEqual(self.led.clear_leds(), [True, False])  # red, green
        time.sleep(1)
        self.assertEqual(self.led.clear_leds(), [False, False])
        time.sleep(1)
        self.assertEqual(self.led.clear_leds(), [False, False])

    def test_combined(self):
        self.assertTrue(self.led.activate_red())
        time.sleep(1)
        self.assertFalse(self.led.activate_green())  # red led is on
        self.assertEqual(self.led.clear_leds(), [True, False])  # red, green
        time.sleep(2)
        self.assertEqual(self.led.clear_leds(), [False, False])
        self.assertTrue(self.led.activate_green())
        self.assertTrue(self.led.activate_red())  # green led is on
        self.assertEqual(self.led.clear_leds(), [True, True])
        time.sleep(3)
        self.assertEqual(self.led.clear_leds(), [False, False])


if __name__ == '__main__':
    unittest.main()
