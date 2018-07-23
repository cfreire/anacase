import unittest
import config


class TestConfigMethods(unittest.TestCase):

    def test_error_file_name(self):
        try:
            config.Config('config.xxx')
        except ValueError:
            self.assertRaises(ValueError)

    def test_section(self):
        cfg2 = config.Config('config.ini')
        self.assertIsNone(cfg2.section('XXX'))
        self.assertEqual(cfg2.section('GLOBAL'), {'log_level': 'DEBUG'})

    def test_keys(self):
        cfg3 = config.Config('config.ini')
        cfg3.section('CONFIG')
        self.assertIsNone(cfg3.key('XXX'))
        self.assertEqual(cfg3.key('author'), 'César Freire')
        self.assertEqual(eval(cfg3.key('version')), 1.0)


if __name__ == '__main__':
    unittest.main()
