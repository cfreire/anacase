import unittest
import config


class TestConfigMethods(unittest.TestCase):

    def test_error_file_name(self):
        try:
            config.init('config.xxx')
        except ValueError:
            self.assertRaises(ValueError)

    def test_section(self):
        config.init('config.ini')
        self.assertIsNone(config.set_section('XXX'))
        self.assertEqual(config.set_section('GLOBAL'), {'log_level': 'DEBUG'})

    def test_keys(self):
        config.init('config.ini')
        config.set_section('CONFIG')
        try:
            config.key['XXX']
        except KeyError:
            self.assertRaises(KeyError)
        self.assertEqual(config.key['author'], 'César Freire')
        self.assertEqual(eval(config.key['version']), 1.0)


if __name__ == '__main__':
    unittest.main()
