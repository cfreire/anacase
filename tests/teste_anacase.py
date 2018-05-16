import unittest
import anacase


class TestAnaCaseMethods(unittest.TestCase):

    def test_get_argument(self):
        self.assertEqual(anacase.get_start_arguments()['config_file'], anacase._configfile_)
        self.assertEqual(anacase.get_start_arguments()['log_file'], anacase._logfile_)


if __name__ == '__main__':
    unittest.main()
