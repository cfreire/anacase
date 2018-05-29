import unittest
import config


class TestConfigMethods(unittest.TestCase):

    def setUp(self):
        self.cfg = config.Config('../anacase.ini')

    def test_invalid_section(self):
        self.assertIsNone(self.cfg.get_str('CAASDMA', '_camera_id'))

    def test_get_int(self):
        self.assertEqual(self.cfg.get_int('CAMERA', 'camera_id'), 0)
        self.assertIsNone(self.cfg.get_int('CAMERA', 'cammesra'))  # warning
        self.assertIsNone(self.cfg.get_int('CAMERA',  'window_title'))  # warning

    def test_get_str(self):
        self.assertEqual(self.cfg.get_str('CAMERA', 'window_title'), 'ANACASE')
        self.assertIsNone(self.cfg.get_str('CAMERA', 'tittles')) # warning

    def test_get_float(self):
        self.assertEqual(self.cfg.get_float('CAMERA', 'time_min_delta'), 2.8)
        self.assertIsNone(self.cfg.get_float('CAMERA', 'ttimmes'))  # warning
        self.assertIsNone(self.cfg.get_float('CAMERA', 'window_title'))  # warning


if __name__ == '__main__':
    unittest.main()
